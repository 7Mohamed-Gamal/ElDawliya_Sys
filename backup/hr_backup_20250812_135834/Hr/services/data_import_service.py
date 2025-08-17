"""
خدمة استيراد البيانات من ملفات Excel وCSV
"""

import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from celery import shared_task

from ..models_integrations import DataImportTemplate, ImportJob

logger = logging.getLogger('hr_data_import')


class DataImportService:
    """خدمة استيراد البيانات"""
    
    def __init__(self, template: DataImportTemplate):
        self.template = template
        self.target_model = self._get_target_model()
        self.field_mapping = template.field_mapping
        self.validation_rules = template.validation_rules
        self.import_settings = template.import_settings
    
    def _get_target_model(self):
        """الحصول على النموذج المستهدف"""
        try:
            app_label, model_name = self.template.target_model.split('.')
            return apps.get_model(app_label, model_name)
        except Exception as e:
            logger.error(f"Failed to get target model {self.template.target_model}: {e}")
            raise ValueError(f"نموذج غير صحيح: {self.template.target_model}")
    
    def process_import_file(self, file_path: str, import_job: ImportJob) -> Dict[str, Any]:
        """معالجة ملف الاستيراد"""
        try:
            # قراءة الملف
            data = self._read_file(file_path)
            
            if data is None:
                return {'success': False, 'error': 'فشل في قراءة الملف'}
            
            # تحديث حالة المهمة
            import_job.status = 'processing'
            import_job.total_rows = len(data)
            import_job.started_at = timezone.now()
            import_job.save()
            
            # التحقق من صحة البيانات
            validation_result = self._validate_data(data, import_job)
            
            if not validation_result['success']:
                import_job.status = 'failed'
                import_job.completed_at = timezone.now()
                import_job.save()
                return validation_result
            
            # استيراد البيانات
            import_result = self._import_data(data, import_job)
            
            # تحديث حالة المهمة النهائية
            import_job.status = 'completed' if import_result['success'] else 'failed'
            import_job.completed_at = timezone.now()
            import_job.result_summary = import_result
            import_job.save()
            
            return import_result
            
        except Exception as e:
            logger.error(f"Import processing failed: {e}")
            import_job.status = 'failed'
            import_job.completed_at = timezone.now()
            import_job.save()
            return {'success': False, 'error': str(e)}
    
    def _read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """قراءة الملف حسب النوع"""
        try:
            if self.template.import_format == 'excel':
                return pd.read_excel(file_path)
            elif self.template.import_format == 'csv':
                encoding = self.import_settings.get('encoding', 'utf-8')
                delimiter = self.import_settings.get('delimiter', ',')
                return pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
            elif self.template.import_format == 'json':
                return pd.read_json(file_path)
            else:
                logger.error(f"Unsupported import format: {self.template.import_format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def _validate_data(self, data: pd.DataFrame, import_job: ImportJob) -> Dict[str, Any]:
        """التحقق من صحة البيانات"""
        try:
            import_job.status = 'validating'
            import_job.save()
            
            validation_errors = []
            
            # التحقق من وجود الأعمدة المطلوبة
            required_columns = [
                file_col for file_col, model_field in self.field_mapping.items()
                if self.validation_rules.get(model_field, {}).get('required', False)
            ]
            
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                validation_errors.append({
                    'type': 'missing_columns',
                    'message': f'أعمدة مطلوبة مفقودة: {", ".join(missing_columns)}'
                })
            
            # التحقق من صحة البيانات في كل صف
            for index, row in data.iterrows():
                row_errors = self._validate_row(row, index + 1)
                validation_errors.extend(row_errors)
                
                # تحديث التقدم
                progress = int((index + 1) / len(data) * 50)  # 50% للتحقق
                import_job.progress_percentage = progress
                import_job.save()
            
            # حفظ أخطاء التحقق
            import_job.validation_errors = validation_errors
            import_job.save()
            
            if validation_errors:
                return {
                    'success': False,
                    'error': 'فشل في التحقق من البيانات',
                    'validation_errors': validation_errors
                }
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_row(self, row: pd.Series, row_number: int) -> List[Dict[str, Any]]:
        """التحقق من صحة صف واحد"""
        errors = []
        
        for file_column, model_field in self.field_mapping.items():
            if file_column not in row.index:
                continue
            
            value = row[file_column]
            field_rules = self.validation_rules.get(model_field, {})
            
            # التحقق من القيم المطلوبة
            if field_rules.get('required', False) and pd.isna(value):
                errors.append({
                    'row': row_number,
                    'column': file_column,
                    'field': model_field,
                    'type': 'required',
                    'message': f'القيمة مطلوبة في العمود {file_column}'
                })
                continue
            
            if pd.isna(value):
                continue
            
            # التحقق من نوع البيانات
            data_type = field_rules.get('data_type')
            if data_type:
                validation_error = self._validate_data_type(value, data_type, row_number, file_column, model_field)
                if validation_error:
                    errors.append(validation_error)
            
            # التحقق من القيم المسموحة
            allowed_values = field_rules.get('allowed_values')
            if allowed_values and value not in allowed_values:
                errors.append({
                    'row': row_number,
                    'column': file_column,
                    'field': model_field,
                    'type': 'invalid_value',
                    'message': f'قيمة غير مسموحة: {value}. القيم المسموحة: {", ".join(allowed_values)}'
                })
            
            # التحقق من الطول
            max_length = field_rules.get('max_length')
            if max_length and isinstance(value, str) and len(value) > max_length:
                errors.append({
                    'row': row_number,
                    'column': file_column,
                    'field': model_field,
                    'type': 'max_length',
                    'message': f'النص طويل جداً. الحد الأقصى: {max_length} حرف'
                })
            
            # التحقق من النمط (regex)
            pattern = field_rules.get('pattern')
            if pattern and isinstance(value, str):
                import re
                if not re.match(pattern, value):
                    errors.append({
                        'row': row_number,
                        'column': file_column,
                        'field': model_field,
                        'type': 'pattern',
                        'message': f'تنسيق غير صحيح للقيمة: {value}'
                    })
        
        return errors
    
    def _validate_data_type(self, value: Any, expected_type: str, row_number: int, column: str, field: str) -> Optional[Dict[str, Any]]:
        """التحقق من نوع البيانات"""
        try:
            if expected_type == 'integer':
                int(value)
            elif expected_type == 'float':
                float(value)
            elif expected_type == 'date':
                pd.to_datetime(value)
            elif expected_type == 'email':
                from django.core.validators import validate_email
                validate_email(str(value))
            elif expected_type == 'boolean':
                if str(value).lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'نعم', 'لا']:
                    raise ValueError("Invalid boolean value")
            
            return None
            
        except (ValueError, ValidationError):
            return {
                'row': row_number,
                'column': column,
                'field': field,
                'type': 'data_type',
                'message': f'نوع بيانات غير صحيح. متوقع: {expected_type}, موجود: {type(value).__name__}'
            }
    
    def _import_data(self, data: pd.DataFrame, import_job: ImportJob) -> Dict[str, Any]:
        """استيراد البيانات إلى قاعدة البيانات"""
        try:
            import_job.status = 'importing'
            import_job.save()
            
            successful_rows = 0
            failed_rows = 0
            import_errors = []
            
            for index, row in data.iterrows():
                try:
                    with transaction.atomic():
                        # تحويل البيانات
                        model_data = self._transform_row_data(row)
                        
                        # إنشاء أو تحديث السجل
                        if self.import_settings.get('update_existing', False):
                            obj, created = self._create_or_update_record(model_data)
                        else:
                            obj = self._create_record(model_data)
                            created = True
                        
                        successful_rows += 1
                        
                except Exception as e:
                    failed_rows += 1
                    import_errors.append({
                        'row': index + 1,
                        'error': str(e),
                        'data': row.to_dict()
                    })
                    logger.error(f"Failed to import row {index + 1}: {e}")
                
                # تحديث التقدم
                progress = 50 + int((index + 1) / len(data) * 50)  # 50% للاستيراد
                import_job.progress_percentage = progress
                import_job.processed_rows = index + 1
                import_job.successful_rows = successful_rows
                import_job.failed_rows = failed_rows
                import_job.save()
            
            # حفظ أخطاء الاستيراد
            import_job.import_errors = import_errors
            import_job.save()
            
            return {
                'success': True,
                'total_rows': len(data),
                'successful_rows': successful_rows,
                'failed_rows': failed_rows,
                'import_errors': import_errors
            }
            
        except Exception as e:
            logger.error(f"Data import failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _transform_row_data(self, row: pd.Series) -> Dict[str, Any]:
        """تحويل بيانات الصف إلى تنسيق النموذج"""
        model_data = {}
        
        for file_column, model_field in self.field_mapping.items():
            if file_column in row.index and not pd.isna(row[file_column]):
                value = row[file_column]
                
                # تطبيق تحويلات البيانات
                transformed_value = self._apply_transformations(value, model_field)
                model_data[model_field] = transformed_value
        
        return model_data
    
    def _apply_transformations(self, value: Any, field_name: str) -> Any:
        """تطبيق تحويلات البيانات"""
        field_rules = self.validation_rules.get(field_name, {})
        
        # تحويل نوع البيانات
        data_type = field_rules.get('data_type')
        if data_type == 'integer':
            return int(value)
        elif data_type == 'float':
            return float(value)
        elif data_type == 'date':
            return pd.to_datetime(value).date()
        elif data_type == 'datetime':
            return pd.to_datetime(value)
        elif data_type == 'boolean':
            return str(value).lower() in ['true', '1', 'yes', 'نعم']
        
        # تطبيق تحويلات مخصصة
        transformations = field_rules.get('transformations', [])
        for transformation in transformations:
            if transformation['type'] == 'replace':
                value = str(value).replace(transformation['from'], transformation['to'])
            elif transformation['type'] == 'upper':
                value = str(value).upper()
            elif transformation['type'] == 'lower':
                value = str(value).lower()
            elif transformation['type'] == 'strip':
                value = str(value).strip()
        
        return value
    
    def _create_record(self, model_data: Dict[str, Any]):
        """إنشاء سجل جديد"""
        return self.target_model.objects.create(**model_data)
    
    def _create_or_update_record(self, model_data: Dict[str, Any]) -> Tuple[Any, bool]:
        """إنشاء أو تحديث سجل"""
        # تحديد الحقول الفريدة للبحث
        unique_fields = self.import_settings.get('unique_fields', ['id'])
        
        # بناء معايير البحث
        lookup_criteria = {}
        for field in unique_fields:
            if field in model_data:
                lookup_criteria[field] = model_data[field]
        
        if lookup_criteria:
            return self.target_model.objects.update_or_create(
                defaults=model_data,
                **lookup_criteria
            )
        else:
            # إذا لم توجد معايير بحث، إنشاء سجل جديد
            return self.target_model.objects.create(**model_data), True
    
    def generate_template_file(self) -> str:
        """إنتاج ملف قالب للتحميل"""
        try:
            import os
            from django.conf import settings
            
            # إنشاء DataFrame فارغ مع الأعمدة المطلوبة
            columns = list(self.field_mapping.keys())
            df = pd.DataFrame(columns=columns)
            
            # إضافة صف مثال
            example_row = {}
            for file_column, model_field in self.field_mapping.items():
                field_rules = self.validation_rules.get(model_field, {})
                data_type = field_rules.get('data_type', 'string')
                
                if data_type == 'integer':
                    example_row[file_column] = 123
                elif data_type == 'float':
                    example_row[file_column] = 123.45
                elif data_type == 'date':
                    example_row[file_column] = '2024-01-01'
                elif data_type == 'email':
                    example_row[file_column] = 'example@company.com'
                elif data_type == 'boolean':
                    example_row[file_column] = 'نعم'
                else:
                    example_row[file_column] = 'مثال'
            
            df = pd.concat([df, pd.DataFrame([example_row])], ignore_index=True)
            
            # حفظ الملف
            filename = f"template_{self.template.name}_{timezone.now().strftime('%Y%m%d')}.xlsx"
            filepath = os.path.join(settings.MEDIA_ROOT, 'templates', filename)
            
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # حفظ ملف Excel مع تنسيق
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='البيانات', index=False)
                
                # تنسيق الورقة
                worksheet = writer.sheets['البيانات']
                
                # تلوين رأس الجدول
                from openpyxl.styles import PatternFill, Font
                header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                header_font = Font(color='FFFFFF', bold=True)
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                
                # ضبط عرض الأعمدة
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate template file: {e}")
            raise e


@shared_task
def process_import_job_async(import_job_id: str):
    """معالجة مهمة الاستيراد بشكل غير متزامن"""
    try:
        import_job = ImportJob.objects.get(id=import_job_id)
        service = DataImportService(import_job.template)
        
        result = service.process_import_file(
            file_path=import_job.data_file.path,
            import_job=import_job
        )
        
        return result
        
    except ImportJob.DoesNotExist:
        logger.error(f"Import job not found: {import_job_id}")
        return {'success': False, 'error': 'مهمة الاستيراد غير موجودة'}
    except Exception as e:
        logger.error(f"Async import processing failed: {e}")
        return {'success': False, 'error': str(e)}