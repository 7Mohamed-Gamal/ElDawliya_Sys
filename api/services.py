import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from .models import GeminiConversation, GeminiMessage
# Temporarily disabled - will be replaced with new modular HR apps
# from Hr.models.employee.employee_models import Employee
# from Hr.models.core.department_models import Department
from inventory.models import TblProducts, TblCategories
from tasks.models import Task
from meetings.models import Meeting

logger = logging.getLogger(__name__)


class GeminiService:
    """Service class for interacting with Google Gemini AI"""

    def __init__(self, user=None):
        self.user = user
        self.api_key = None
        self.model_name = 'gemini-1.5-flash'
        self.config_source = 'none'
        
        # First try to get API key from user configuration
        if user:
            try:
                from .models import AIConfiguration, AIProvider
                
                # Try to get the Gemini provider
                try:
                    provider = AIProvider.objects.get(name='gemini')
                    logger.info(f"Found Gemini provider: {provider.id}")
                    
                    # Try to get user's default Gemini configuration
                    config = AIConfiguration.objects.filter(
                        user=user,
                        provider=provider,
                        is_active=True
                    ).order_by('-is_default').first()
                    
                    if config:
                        self.api_key = config.api_key
                        self.model_name = config.model_name
                        self.config_source = 'user_config'
                        logger.info(f"Using Gemini configuration for user {user.username}, API key: {self.api_key[:5]}..., model: {self.model_name}")
                    else:
                        logger.warning(f"No active Gemini configuration found for user {user.username}")
                
                except AIProvider.DoesNotExist:
                    logger.warning("Gemini provider does not exist in the database")
                    
                    # Create the provider
                    provider = AIProvider.objects.create(
                        name='gemini',
                        display_name='Google Gemini',
                        description='Google Gemini AI models',
                        is_active=True,
                        requires_api_key=True
                    )
                    logger.info(f"Created Gemini provider: {provider.id}")
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                logger.warning(f"Error getting user Gemini configuration: {str(e)}\n{error_traceback}")
        
        # If no API key from user config, try environment variable
        if not self.api_key:
            env_api_key = os.getenv('GEMINI_API_KEY')
            if env_api_key:
                self.api_key = env_api_key
                self.config_source = 'environment'
                env_model = os.getenv('GEMINI_MODEL')
                if env_model:
                    self.model_name = env_model
                logger.info(f"Using Gemini configuration from environment variables, API key: {self.api_key[:5]}..., model: {self.model_name}")
        
        # Check if configuration is valid
        self.is_configured = bool(self.api_key and GEMINI_AVAILABLE)

        if self.is_configured:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini AI configured successfully with model: {self.model_name}")
            except Exception as e:
                self.is_configured = False
                logger.error(f"Failed to configure Gemini AI: {str(e)}")
        else:
            missing = []
            if not self.api_key:
                missing.append("API key")
            if not GEMINI_AVAILABLE:
                missing.append("genai library")
            logger.warning(f"Gemini AI is not properly configured. Missing: {', '.join(missing)}")

    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.is_configured

    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response using Gemini AI"""
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Gemini AI is not configured properly',
                'response': None,
                'tokens_used': 0
            }

        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            )

            # Safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Extract response text
            response_text = response.text if response.text else "عذراً، لم أتمكن من إنتاج رد مناسب."

            # Estimate tokens used (rough estimation)
            tokens_used = len(prompt.split()) + len(response_text.split())

            return {
                'success': True,
                'response': response_text,
                'tokens_used': tokens_used,
                'error': None
            }

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error generating Gemini response: {str(e)}\n{error_traceback}")
            return {
                'success': False,
                'error': f"Error generating Gemini response: {str(e)}",
                'traceback': error_traceback,
                'response': None,
                'tokens_used': 0,
                'model': self.model_name,
                'api_source': self.config_source
            }

    def chat_with_context(self, user, message: str, conversation_id: Optional[str] = None,
                         temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Chat with Gemini AI maintaining conversation context"""
        try:
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = GeminiConversation.objects.get(
                        id=conversation_id,
                        user=user,
                        is_active=True
                    )
                except GeminiConversation.DoesNotExist:
                    conversation = GeminiConversation.objects.create(
                        user=user,
                        title=message[:50] + "..." if len(message) > 50 else message
                    )
            else:
                conversation = GeminiConversation.objects.create(
                    user=user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )

            # Build context from previous messages
            previous_messages = conversation.messages.order_by('timestamp')[:10]  # Last 10 messages
            context = ""

            if previous_messages.exists():
                context = "السياق السابق للمحادثة:\n"
                for msg in previous_messages:
                    role_ar = "المستخدم" if msg.role == "user" else "المساعد"
                    context += f"{role_ar}: {msg.content}\n"
                context += "\n"

            # Add system context about the ElDawliya system
            system_context = """
أنت مساعد ذكي لنظام الدولية للإدارة. النظام يحتوي على:
- إدارة الموارد البشرية (الموظفين والأقسام)
- إدارة المخزون (المنتجات والموردين)
- إدارة المهام والاجتماعات
- نظام المشتريات والطلبات

أنت متكامل مع قاعدة بيانات النظام ويمكنك الوصول إلى المعلومات الفعلية وتقديم تحليلات وتقارير.

يرجى تقديم إجابات مفيدة ودقيقة باللغة العربية.
"""
            
            # First, detect if this is a system data analysis request
            try:
                # Check for inventory analysis queries
                if any(keyword in message.lower() for keyword in [
                    'المخزون', 'الاصناف', 'المنتجات', 'البضاعة', 'الرصيد', 'الأصناف', 
                    'ناقص', 'الكميات', 'منتهية الصلاحية', 'منخفضة', 'المستودع', 'حد أدنى', 'قائمة'
                ]):
                    # Initialize data service just once for better performance
                    data_service = DataAnalysisService(user=user)
                    
                    # First check for low stock items since it's the most specific
                    if any(keyword in message.lower() for keyword in [
                        'منخفض', 'أقل من', 'قليل', 'ناقص', 'الحد الأدنى', 'نواقص', 'نفذت', 
                        'الكميات القليلة', 'تحت الحد', 'الأصناف الناقصة'
                    ]):
                        # Add info about low stock items to the system context
                        system_context += "\n\n--- معلومات المخزون ---\n"
                        system_context += "قمت بالبحث عن الأصناف منخفضة المخزون في قاعدة البيانات. "
                        
                        # Try to get low stock items
                        try:
                            low_stock_data = data_service.get_low_stock_items()
                            if low_stock_data['success'] and low_stock_data['low_stock_count'] > 0:
                                system_context += f"وجدت {low_stock_data['low_stock_count']} من الأصناف منخفضة المخزون. "
                                system_context += "تفاصيل الأصناف:\n"
                                
                                # Add information about each item
                                for item in low_stock_data['items'][:5]:  # Limit to first 5 for brevity
                                    system_context += f"- {item['اسم الصنف']}: الرصيد الحالي {item['الرصيد الحالي']} "
                                    system_context += f"(الحد الأدنى {item['الحد الأدنى']})\n"
                                
                                if len(low_stock_data['items']) > 5:
                                    system_context += f"... وهناك {len(low_stock_data['items']) - 5} أصناف أخرى منخفضة المخزون.\n"
                            else:
                                system_context += "لم أجد أي أصناف منخفضة المخزون في النظام."
                        except Exception as e:
                            logger.error(f"Error fetching low stock items: {str(e)}")
                            system_context += "واجهت مشكلة في استعلام البيانات من النظام."
                    
                    # General inventory analysis as a fallback
                    else:
                        # Add general inventory info to the system context
                        system_context += "\n\n--- معلومات عامة عن المخزون ---\n"
                        try:
                            inventory_data = data_service.analyze_inventory()
                            if inventory_data['success']:
                                summary = inventory_data['data_summary']
                                system_context += f"إجمالي المنتجات في المخزون: {summary['total_products']}\n"
                                system_context += f"عدد الأصناف منخفضة المخزون: {summary['low_stock_items']}\n"
                                
                                # Add category distribution if available
                                if 'categories' in summary and len(summary['categories']) > 0:
                                    system_context += "توزيع الفئات:\n"
                                    for cat in summary['categories'][:3]:  # Show top 3 categories
                                        if isinstance(cat, dict) and 'name' in cat and 'product_count' in cat:
                                            system_context += f"- {cat['name']}: {cat['product_count']} صنف\n"
                            else:
                                system_context += "لم أتمكن من تحليل بيانات المخزون."
                        except Exception as e:
                            logger.error(f"Error analyzing inventory: {str(e)}")
                            system_context += "واجهت مشكلة في تحليل بيانات المخزون."
            except Exception as e:
                logger.error(f"Error in data analysis integration: {str(e)}")
                # Continue without integrated data if there's an error
            
            # Combine context with current message
            full_prompt = f"{system_context}\n{context}المستخدم: {message}\nالمساعد:"

            # Generate response
            result = self.generate_response(full_prompt, temperature, max_tokens)

            if result['success']:
                # Save user message
                GeminiMessage.objects.create(
                    conversation=conversation,
                    role='user',
                    content=message
                )

                # Save assistant response
                GeminiMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=result['response'],
                    tokens_used=result['tokens_used']
                )

                # Update conversation timestamp
                conversation.updated_at = timezone.now()
                conversation.save()

                return {
                    'success': True,
                    'response': result['response'],
                    'conversation_id': str(conversation.id),
                    'tokens_used': result['tokens_used']
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in chat_with_context: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': None,
                'tokens_used': 0
            }


class DataAnalysisService:
    """Service for analyzing system data with Gemini AI"""

    def __init__(self, user=None):
        self.gemini_service = GeminiService(user=user)
        self.user = user

    def analyze_employees(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze employee data"""
        try:
            # Get employee data
            employees = Employee.objects.all()
            if filters:
                if 'department' in filters:
                    employees = employees.filter(department__dept_name__icontains=filters['department'])
                if 'status' in filters:
                    employees = employees.filter(emp_status=filters['status'])

            # Prepare data summary
            total_employees = employees.count()
            departments = employees.values('department__dept_name').annotate(count=Count('id'))
            status_distribution = employees.values('emp_status').annotate(count=Count('id'))

            # Create analysis prompt
            prompt = f"""
قم بتحليل بيانات الموظفين التالية:
- إجمالي عدد الموظفين: {total_employees}
- توزيع الأقسام: {list(departments)}
- توزيع الحالات: {list(status_distribution)}

يرجى تقديم:
1. ملخص عام
2. الاتجاهات الملاحظة
3. التوصيات لتحسين إدارة الموارد البشرية
"""

            result = self.gemini_service.generate_response(prompt)

            if result['success']:
                return {
                    'success': True,
                    'analysis': result['response'],
                    'data_summary': {
                        'total_employees': total_employees,
                        'departments': list(departments),
                        'status_distribution': list(status_distribution)
                    },
                    'insights': self._extract_insights(result['response']),
                    'recommendations': self._extract_recommendations(result['response'])
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error analyzing employees: {str(e)}")
            return {'success': False, 'error': str(e)}

    def analyze_inventory(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze inventory data"""
        try:
            # First try with the local models (preferred)
            try:
                from inventory.models_local import Product, Category
                
                products = Product.objects.all()
                if filters:
                    if 'category' in filters:
                        products = products.filter(category__name__icontains=filters['category'])
                    if 'low_stock' in filters and filters['low_stock']:
                        from django.db import models as django_models
                        products = products.filter(quantity__lte=django_models.F('minimum_threshold'))

                # Prepare data summary
                total_products = products.count()
                categories = Category.objects.annotate(product_count=Count('products')).values('name', 'product_count')
                from django.db import models as django_models
                low_stock_items = products.filter(quantity__lte=django_models.F('minimum_threshold')).count()

            except (ImportError, ModuleNotFoundError):
                # Fallback to the original models if local models aren't available
                products = TblProducts.objects.all()
                if filters:
                    if 'category' in filters:
                        products = products.filter(cat_name__icontains=filters['category'])
                    if 'low_stock' in filters and filters['low_stock']:
                        from django.db import models as django_models
                        products = products.filter(qte_in_stock__lte=django_models.F('minimum_threshold'))

                # Prepare data summary
                total_products = products.count()
                categories = products.values('cat_name').annotate(count=Count('product_id'))
                from django.db import models as django_models
                low_stock_items = products.filter(qte_in_stock__lte=django_models.F('minimum_threshold')).count()

            # Create analysis prompt
            prompt = f"""
قم بتحليل بيانات المخزون التالية:
- إجمالي عدد المنتجات: {total_products}
- توزيع الفئات: {list(categories)}
- عدد المنتجات منخفضة المخزون: {low_stock_items}

يرجى تقديم:
1. تحليل حالة المخزون
2. التحديات المحتملة
3. توصيات لتحسين إدارة المخزون
"""

            result = self.gemini_service.generate_response(prompt)

            if result['success']:
                return {
                    'success': True,
                    'analysis': result['response'],
                    'data_summary': {
                        'total_products': total_products,
                        'categories': list(categories),
                        'low_stock_items': low_stock_items
                    },
                    'insights': self._extract_insights(result['response']),
                    'recommendations': self._extract_recommendations(result['response'])
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error analyzing inventory: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    def get_low_stock_items(self) -> Dict[str, Any]:
        """
        Get items with stock below minimum threshold and generate a report
        """
        try:
            # Try with local models first
            try:
                from inventory.models_local import Product
                
                from django.db import models as django_models
                
                low_stock_items = Product.objects.filter(
                    quantity__lt=django_models.F('minimum_threshold'),
                    minimum_threshold__gt=0
                ).values('product_id', 'name', 'quantity', 'minimum_threshold', 'category__name', 'unit__name')
                
                # Format output for display
                formatted_items = []
                for item in low_stock_items:
                    formatted_items.append({
                        'رقم الصنف': item['product_id'],
                        'اسم الصنف': item['name'],
                        'الرصيد الحالي': float(item['quantity']),
                        'الحد الأدنى': float(item['minimum_threshold']),
                        'التصنيف': item['category__name'] or 'غير محدد',
                        'وحدة القياس': item['unit__name'] or 'غير محدد',
                        'النقص': float(item['minimum_threshold']) - float(item['quantity'])
                    })
                    
            except (ImportError, ModuleNotFoundError):
                # Fallback to original models
                from inventory.models import TblProducts
                
                from django.db import models as django_models
                
                low_stock_items = TblProducts.objects.filter(
                    qte_in_stock__lt=django_models.F('minimum_threshold'),
                    minimum_threshold__gt=0
                ).values('product_id', 'product_name', 'qte_in_stock', 'minimum_threshold', 'cat_name', 'unit_name')
                
                # Format output for display
                formatted_items = []
                for item in low_stock_items:
                    formatted_items.append({
                        'رقم الصنف': item['product_id'],
                        'اسم الصنف': item['product_name'],
                        'الرصيد الحالي': float(item['qte_in_stock']) if item['qte_in_stock'] else 0,
                        'الحد الأدنى': float(item['minimum_threshold']) if item['minimum_threshold'] else 0,
                        'التصنيف': item['cat_name'] or 'غير محدد',
                        'وحدة القياس': item['unit_name'] or 'غير محدد',
                        'النقص': (float(item['minimum_threshold']) if item['minimum_threshold'] else 0) - 
                                 (float(item['qte_in_stock']) if item['qte_in_stock'] else 0)
                    })
            
            # Generate report with Gemini
            if formatted_items:
                items_json = json.dumps(formatted_items, ensure_ascii=False, indent=2)
                
                prompt = f"""
أحتاج تقرير مفصل وتحليل للأصناف منخفضة المخزون في المستودع. إليك البيانات:

{items_json}

يرجى إنشاء تقرير مفصل يتضمن:
1. ملخص عام لحالة المخزون (عدد الأصناف منخفضة المخزون، إجمالي النقص)
2. تصنيف الأصناف حسب أولوية التوريد
3. توصيات للإدارة حول الخطوات التالية

ملاحظة: قدم التقرير بتنسيق واضح ومنظم مع عناوين وجداول واضحة.
"""
                
                result = self.gemini_service.generate_response(prompt, temperature=0.2)
                
                if result['success']:
                    return {
                        'success': True,
                        'report': result['response'],
                        'low_stock_count': len(formatted_items),
                        'items': formatted_items
                    }
                else:
                    return result
            else:
                return {
                    'success': True,
                    'report': "لا توجد أصناف منخفضة المخزون في المستودع حاليًا.",
                    'low_stock_count': 0,
                    'items': []
                }
                
        except Exception as e:
            logger.error(f"Error generating low stock report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_insights(self, text: str) -> List[str]:
        """Extract insights from analysis text"""
        # Simple extraction - can be improved with NLP
        insights = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['ملاحظة', 'اتجاه', 'نمط', 'تحليل']):
                insights.append(line.strip())
        return insights[:5]  # Return top 5 insights

    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from analysis text"""
        # Simple extraction - can be improved with NLP
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['توصية', 'يُنصح', 'يجب', 'يمكن تحسين']):
                recommendations.append(line.strip())
        return recommendations[:5]  # Return top 5 recommendations


class OllamaService:
    """Service class for interacting with Ollama AI (Local)"""

    def __init__(self, user=None):
        self.user = user
        self.api_url = 'http://localhost:11434'  # Default Ollama URL
        self.model_name = 'llama2'
        self.config_source = 'none'
        self.is_configured = False

        # Try to get user configuration
        if user:
            try:
                from .models import AIConfiguration, AIProvider

                # Try to get the Ollama provider
                try:
                    provider = AIProvider.objects.get(name='ollama')
                    logger.info(f"Found Ollama provider: {provider.id}")

                    # Try to get user's Ollama configuration
                    config = AIConfiguration.objects.filter(
                        user=user,
                        provider=provider,
                        is_active=True
                    ).order_by('-is_default').first()

                    if config:
                        # For Ollama, api_key field can store the base URL
                        if config.api_key:
                            self.api_url = config.api_key
                        self.model_name = config.model_name or 'llama2'
                        self.config_source = 'user_config'
                        logger.info(f"Using Ollama configuration for user {user.username}, URL: {self.api_url}, model: {self.model_name}")
                    else:
                        logger.warning(f"No active Ollama configuration found for user {user.username}")

                except AIProvider.DoesNotExist:
                    logger.warning("Ollama provider does not exist in the database")

            except Exception as e:
                logger.warning(f"Error getting user Ollama configuration: {str(e)}")

        # Test connection to Ollama
        self.is_configured = self._test_connection()

    def _test_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Ollama service is available at {self.api_url}")
                return True
            else:
                logger.warning(f"Ollama service returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"Cannot connect to Ollama service at {self.api_url}: {str(e)}")
            return False

    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        return self.is_configured

    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response using Ollama AI"""
        if not self.is_configured:
            return {
                'success': False,
                'error': f'Ollama AI is not available at {self.api_url}',
                'response': None,
                'tokens_used': 0
            }

        try:
            # Prepare the request payload
            payload = {
                'model': self.model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens
                }
            }

            # Make the API call
            response = requests.post(
                f"{self.api_url}/api/generate",
                json=payload,
                timeout=60  # Ollama can be slow
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')

                # Estimate tokens (rough approximation)
                tokens_used = len(response_text.split()) + len(prompt.split())

                logger.info(f"Ollama response generated successfully, estimated tokens: {tokens_used}")

                return {
                    'success': True,
                    'response': response_text,
                    'tokens_used': tokens_used,
                    'model': self.model_name
                }
            else:
                error_msg = f"Ollama API returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'response': None,
                    'tokens_used': 0
                }

        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'response': None,
                'tokens_used': 0
            }
        except Exception as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'response': None,
                'tokens_used': 0
            }

    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        if not self.is_configured:
            return []

        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                logger.info(f"Available Ollama models: {models}")
                return models
            else:
                logger.warning(f"Failed to get Ollama models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting Ollama models: {str(e)}")
            return []


class UnifiedAIService:
    """Unified service for handling multiple AI providers"""

    def __init__(self, user=None):
        self.user = user
        self.active_provider = None
        self.active_service = None

        # Initialize available services
        self.services = {
            'gemini': GeminiService(user=user),
            'ollama': OllamaService(user=user),
        }

        # Find the default or first available provider
        self._initialize_active_provider()

    def _initialize_active_provider(self):
        """Initialize the active AI provider"""
        if not self.user:
            # Try Ollama first for anonymous users (local)
            if self.services['ollama'].is_available():
                self.active_provider = 'ollama'
                self.active_service = self.services['ollama']
                return
            elif self.services['gemini'].is_available():
                self.active_provider = 'gemini'
                self.active_service = self.services['gemini']
                return
        else:
            # For authenticated users, check their default configuration
            try:
                from .models import AIConfiguration

                # Get user's default configuration
                default_config = AIConfiguration.objects.filter(
                    user=self.user,
                    is_default=True,
                    is_active=True
                ).select_related('provider').first()

                if default_config:
                    provider_name = default_config.provider.name
                    if provider_name in self.services and self.services[provider_name].is_available():
                        self.active_provider = provider_name
                        self.active_service = self.services[provider_name]
                        logger.info(f"Using default provider {provider_name} for user {self.user.username}")
                        return

                # If no default or default not available, find first available
                for provider_name, service in self.services.items():
                    if service.is_available():
                        self.active_provider = provider_name
                        self.active_service = service
                        logger.info(f"Using first available provider {provider_name} for user {self.user.username}")
                        return

            except Exception as e:
                logger.error(f"Error initializing AI provider for user {self.user.username}: {str(e)}")

        # No provider available
        logger.warning("No AI provider is available")

    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.active_service is not None and self.active_service.is_available()

    def get_active_provider(self) -> Optional[str]:
        """Get the name of the active provider"""
        return self.active_provider

    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response using the active AI provider"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'No AI provider is available',
                'response': None,
                'tokens_used': 0
            }

        result = self.active_service.generate_response(prompt, temperature, max_tokens)
        result['provider'] = self.active_provider
        return result

    def chat_with_context(self, message: str, conversation_id: Optional[str] = None,
                         temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Chat with context using the active provider"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'No AI provider is available',
                'response': None,
                'tokens_used': 0
            }

        # For now, use Gemini's chat_with_context if available, otherwise use simple generate_response
        if self.active_provider == 'gemini' and hasattr(self.active_service, 'chat_with_context'):
            result = self.active_service.chat_with_context(
                user=self.user,
                message=message,
                conversation_id=conversation_id,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # For other providers, use simple response generation
            result = self.generate_response(message, temperature, max_tokens)
            if result['success']:
                result['conversation_id'] = conversation_id or 'simple_chat'

        result['provider'] = self.active_provider
        return result

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status"""
        providers = []
        for name, service in self.services.items():
            providers.append({
                'name': name,
                'available': service.is_available(),
                'is_active': name == self.active_provider
            })
        return providers
