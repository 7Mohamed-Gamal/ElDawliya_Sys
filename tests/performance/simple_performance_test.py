#!/usr/bin/env python
"""
اختبار أداء بسيط ومستقل
Simple standalone performance test

يقوم بإجراء اختبارات أداء أساسية بدون الاعتماد على جميع تبعيات Django
"""
import os
import sys
import time
import statistics
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_system_resources():
    """اختبار موارد النظام"""
    print("🖥️  اختبار موارد النظام:")
    
    # معلومات المعالج
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # معلومات الذاكرة
    memory = psutil.virtual_memory()
    memory_total = memory.total / 1024 / 1024 / 1024  # GB
    memory_available = memory.available / 1024 / 1024 / 1024  # GB
    memory_percent = memory.percent
    
    # معلومات القرص
    disk = psutil.disk_usage('/')
    disk_total = disk.total / 1024 / 1024 / 1024  # GB
    disk_free = disk.free / 1024 / 1024 / 1024  # GB
    disk_percent = (disk.used / disk.total) * 100
    
    print(f"   عدد المعالجات: {cpu_count}")
    print(f"   استهلاك المعالج: {cpu_percent:.1f}%")
    print(f"   إجمالي الذاكرة: {memory_total:.2f} GB")
    print(f"   الذاكرة المتاحة: {memory_available:.2f} GB")
    print(f"   استهلاك الذاكرة: {memory_percent:.1f}%")
    print(f"   إجمالي القرص: {disk_total:.2f} GB")
    print(f"   القرص المتاح: {disk_free:.2f} GB")
    print(f"   استهلاك القرص: {disk_percent:.1f}%")
    
    # تقييم الموارد
    issues = []
    if cpu_percent > 80:
        issues.append("استهلاك مرتفع للمعالج")
    if memory_percent > 80:
        issues.append("استهلاك مرتفع للذاكرة")
    if disk_percent > 90:
        issues.append("مساحة قرص منخفضة")
    
    if issues:
        print(f"   ⚠️  تحذيرات: {', '.join(issues)}")
    else:
        print(f"   ✅ موارد النظام في حالة جيدة")
    
    return {
        'cpu_count': cpu_count,
        'cpu_percent': cpu_percent,
        'memory_total_gb': memory_total,
        'memory_available_gb': memory_available,
        'memory_percent': memory_percent,
        'disk_total_gb': disk_total,
        'disk_free_gb': disk_free,
        'disk_percent': disk_percent,
        'issues': issues
    }

def test_memory_performance():
    """اختبار أداء الذاكرة"""
    print("\n🧠 اختبار أداء الذاكرة:")
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # اختبار تخصيص الذاكرة
    print("   اختبار تخصيص الذاكرة...")
    start_time = time.time()
    
    # تخصيص قوائم كبيرة
    large_lists = []
    for i in range(10):
        large_list = list(range(100000))  # 100k عنصر
        large_lists.append(large_list)
    
    allocation_time = (time.time() - start_time) * 1000
    current_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = current_memory - initial_memory
    
    print(f"   وقت التخصيص: {allocation_time:.2f}ms")
    print(f"   زيادة الذاكرة: {memory_increase:.2f}MB")
    
    # اختبار تحرير الذاكرة
    start_time = time.time()
    del large_lists
    import gc
    gc.collect()
    
    cleanup_time = (time.time() - start_time) * 1000
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_freed = current_memory - final_memory
    
    print(f"   وقت التحرير: {cleanup_time:.2f}ms")
    print(f"   الذاكرة المحررة: {memory_freed:.2f}MB")
    
    # تقييم الأداء
    if allocation_time < 100:
        print("   ✅ أداء تخصيص الذاكرة ممتاز")
    elif allocation_time < 500:
        print("   ⚠️  أداء تخصيص الذاكرة جيد")
    else:
        print("   ❌ أداء تخصيص الذاكرة بطيء")
    
    return {
        'allocation_time_ms': allocation_time,
        'cleanup_time_ms': cleanup_time,
        'memory_increase_mb': memory_increase,
        'memory_freed_mb': memory_freed
    }

def test_cpu_performance():
    """اختبار أداء المعالج"""
    print("\n⚡ اختبار أداء المعالج:")
    
    def cpu_intensive_task(n):
        """مهمة تستهلك المعالج"""
        result = 0
        for i in range(n):
            result += i ** 2
        return result
    
    # اختبار مهمة واحدة
    print("   اختبار مهمة واحدة...")
    start_time = time.time()
    result = cpu_intensive_task(1000000)
    single_task_time = (time.time() - start_time) * 1000
    
    print(f"   وقت المهمة الواحدة: {single_task_time:.2f}ms")
    
    # اختبار مهام متعددة متسلسلة
    print("   اختبار مهام متعددة متسلسلة...")
    start_time = time.time()
    for _ in range(4):
        cpu_intensive_task(250000)
    sequential_time = (time.time() - start_time) * 1000
    
    print(f"   وقت المهام المتسلسلة: {sequential_time:.2f}ms")
    
    # اختبار مهام متعددة متوازية
    print("   اختبار مهام متعددة متوازية...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(cpu_intensive_task, 250000) for _ in range(4)]
        for future in as_completed(futures):
            future.result()
    
    parallel_time = (time.time() - start_time) * 1000
    
    print(f"   وقت المهام المتوازية: {parallel_time:.2f}ms")
    
    # حساب تحسن الأداء
    if parallel_time < sequential_time:
        improvement = (sequential_time - parallel_time) / sequential_time * 100
        print(f"   ✅ تحسن الأداء بالمعالجة المتوازية: {improvement:.1f}%")
    else:
        print("   ⚠️  المعالجة المتوازية لم تحسن الأداء")
    
    return {
        'single_task_time_ms': single_task_time,
        'sequential_time_ms': sequential_time,
        'parallel_time_ms': parallel_time,
        'parallel_improvement': (sequential_time - parallel_time) / sequential_time * 100 if parallel_time < sequential_time else 0
    }

def test_io_performance():
    """اختبار أداء الإدخال والإخراج"""
    print("\n💾 اختبار أداء الإدخال والإخراج:")
    
    test_file = "performance_test_temp.txt"
    test_data = "هذا نص تجريبي لاختبار أداء الإدخال والإخراج. " * 1000
    
    try:
        # اختبار الكتابة
        print("   اختبار كتابة الملف...")
        start_time = time.time()
        
        with open(test_file, 'w', encoding='utf-8') as f:
            for _ in range(100):
                f.write(test_data)
        
        write_time = (time.time() - start_time) * 1000
        file_size = os.path.getsize(test_file) / 1024 / 1024  # MB
        
        print(f"   وقت الكتابة: {write_time:.2f}ms")
        print(f"   حجم الملف: {file_size:.2f}MB")
        print(f"   سرعة الكتابة: {file_size / (write_time / 1000):.2f}MB/s")
        
        # اختبار القراءة
        print("   اختبار قراءة الملف...")
        start_time = time.time()
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        read_time = (time.time() - start_time) * 1000
        
        print(f"   وقت القراءة: {read_time:.2f}ms")
        print(f"   سرعة القراءة: {file_size / (read_time / 1000):.2f}MB/s")
        
        # تقييم الأداء
        write_speed = file_size / (write_time / 1000)
        read_speed = file_size / (read_time / 1000)
        
        if write_speed > 50:  # أكثر من 50 MB/s
            print("   ✅ أداء كتابة ممتاز")
        elif write_speed > 10:
            print("   ⚠️  أداء كتابة جيد")
        else:
            print("   ❌ أداء كتابة بطيء")
        
        if read_speed > 100:  # أكثر من 100 MB/s
            print("   ✅ أداء قراءة ممتاز")
        elif read_speed > 20:
            print("   ⚠️  أداء قراءة جيد")
        else:
            print("   ❌ أداء قراءة بطيء")
        
        return {
            'write_time_ms': write_time,
            'read_time_ms': read_time,
            'file_size_mb': file_size,
            'write_speed_mbps': write_speed,
            'read_speed_mbps': read_speed
        }
        
    finally:
        # تنظيف الملف التجريبي
        if os.path.exists(test_file):
            os.remove(test_file)

def test_concurrent_operations():
    """اختبار العمليات المتزامنة"""
    print("\n🔄 اختبار العمليات المتزامنة:")
    
    def simple_task(task_id, duration=0.1):
        """مهمة بسيطة"""
        start_time = time.time()
        time.sleep(duration)
        end_time = time.time()
        return {
            'task_id': task_id,
            'duration': (end_time - start_time) * 1000,
            'success': True
        }
    
    # اختبار 10 مهام متزامنة
    print("   اختبار 10 مهام متزامنة...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simple_task, i, 0.1) for i in range(10)]
        results = [future.result() for future in as_completed(futures)]
    
    total_time = (time.time() - start_time) * 1000
    successful_tasks = sum(1 for r in results if r['success'])
    avg_task_duration = statistics.mean([r['duration'] for r in results])
    
    print(f"   الوقت الإجمالي: {total_time:.2f}ms")
    print(f"   المهام الناجحة: {successful_tasks}/10")
    print(f"   متوسط مدة المهمة: {avg_task_duration:.2f}ms")
    
    # تقييم الأداء
    if successful_tasks == 10 and total_time < 200:  # أقل من 200ms
        print("   ✅ أداء العمليات المتزامنة ممتاز")
    elif successful_tasks >= 8 and total_time < 500:
        print("   ⚠️  أداء العمليات المتزامنة جيد")
    else:
        print("   ❌ أداء العمليات المتزامنة بطيء")
    
    return {
        'total_time_ms': total_time,
        'successful_tasks': successful_tasks,
        'avg_task_duration_ms': avg_task_duration,
        'tasks_per_second': 10 / (total_time / 1000)
    }

def generate_performance_report(results):
    """إنتاج تقرير الأداء"""
    print("\n" + "=" * 60)
    print("📋 تقرير الأداء الشامل")
    print("=" * 60)
    
    # تقييم عام
    issues = []
    
    # تحليل موارد النظام
    system = results['system']
    if system['cpu_percent'] > 80:
        issues.append("استهلاك مرتفع للمعالج")
    if system['memory_percent'] > 80:
        issues.append("استهلاك مرتفع للذاكرة")
    if system['disk_percent'] > 90:
        issues.append("مساحة قرص منخفضة")
    
    # تحليل أداء الذاكرة
    memory = results['memory']
    if memory['allocation_time_ms'] > 500:
        issues.append("أداء تخصيص الذاكرة بطيء")
    
    # تحليل أداء المعالج
    cpu = results['cpu']
    if cpu['parallel_improvement'] < 10:
        issues.append("تحسن ضعيف في المعالجة المتوازية")
    
    # تحليل أداء الإدخال والإخراج
    io = results['io']
    if io['write_speed_mbps'] < 10:
        issues.append("أداء كتابة الملفات بطيء")
    if io['read_speed_mbps'] < 20:
        issues.append("أداء قراءة الملفات بطيء")
    
    # تحليل العمليات المتزامنة
    concurrent = results['concurrent']
    if concurrent['successful_tasks'] < 8:
        issues.append("فشل في العمليات المتزامنة")
    
    # التقييم النهائي
    if not issues:
        print("🎉 تقييم عام: ممتاز - النظام يحقق معايير الأداء المطلوبة")
        grade = "A"
    elif len(issues) <= 2:
        print("⚠️  تقييم عام: جيد - يحتاج بعض التحسينات")
        grade = "B"
    else:
        print("🚨 تقييم عام: يحتاج تحسين - مشاكل أداء تحتاج إلى إصلاح")
        grade = "C"
    
    print(f"الدرجة: {grade}")
    
    if issues:
        print(f"\n⚠️  المشاكل المكتشفة:")
        for issue in issues:
            print(f"   - {issue}")
    
    # توصيات التحسين
    print(f"\n💡 توصيات التحسين:")
    
    if system['memory_percent'] > 70:
        print("   - إغلاق التطبيقات غير المستخدمة لتوفير الذاكرة")
    
    if cpu['parallel_improvement'] < 20:
        print("   - تحسين خوارزميات المعالجة المتوازية")
    
    if io['write_speed_mbps'] < 50:
        print("   - استخدام قرص SSD لتحسين أداء الإدخال والإخراج")
    
    if concurrent['successful_tasks'] < 10:
        print("   - مراجعة إدارة الخيوط والعمليات المتزامنة")
    
    print("   - تطبيق تخزين مؤقت للبيانات المتكررة")
    print("   - تحسين استعلامات قاعدة البيانات")
    print("   - مراقبة الأداء بشكل دوري")
    
    return grade, issues

def main():
    """الدالة الرئيسية"""
    print("🎯 اختبار الأداء البسيط - نظام الدولية")
    print("=" * 60)
    print(f"وقت البدء: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    try:
        # تشغيل الاختبارات
        results['system'] = test_system_resources()
        results['memory'] = test_memory_performance()
        results['cpu'] = test_cpu_performance()
        results['io'] = test_io_performance()
        results['concurrent'] = test_concurrent_operations()
        
        # إنتاج التقرير
        grade, issues = generate_performance_report(results)
        
        print(f"\n" + "=" * 60)
        print(f"وقت الانتهاء: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return 0 if grade in ['A', 'B'] else 1
        
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل اختبارات الأداء: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())