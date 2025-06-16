# تطبيق إدارة الاجتماعات (Meetings Application)

## نظرة عامة (Application Overview)

تطبيق إدارة الاجتماعات يوفر نظام شامل لجدولة وإدارة الاجتماعات في نظام الدولية. يتضمن إنشاء الاجتماعات، دعوة المشاركين، تتبع الحضور، إدارة جدول الأعمال، وتسجيل المحاضر مع دعم كامل للغة العربية.

**الغرض الرئيسي**: إدارة شاملة للاجتماعات من التخطيط إلى المتابعة.

## الميزات الرئيسية (Key Features)

### 1. إدارة الاجتماعات (Meeting Management)
- إنشاء وجدولة الاجتماعات
- تحديد المكان والوقت
- إضافة وصف وأهداف الاجتماع
- ربط الاجتماعات بالمشاريع والأقسام
- إعدادات الخصوصية والوصول

### 2. إدارة المشاركين (Participant Management)
- دعوة المشاركين من داخل النظام
- تحديد أدوار المشاركين (منظم، مشارك، مراقب)
- تتبع حالة الدعوات (مقبولة، مرفوضة، معلقة)
- إرسال تذكيرات تلقائية
- إدارة قوائم الحضور

### 3. جدول الأعمال (Agenda Management)
- إنشاء جدول أعمال مفصل
- ترتيب البنود حسب الأولوية
- تحديد الوقت المخصص لكل بند
- تعيين مسؤولين عن البنود
- إضافة مرفقات ووثائق

### 4. تسجيل المحاضر (Minutes Recording)
- تسجيل محاضر الاجتماعات
- تتبع القرارات والتوصيات
- تحديد المهام والمسؤوليات
- إضافة الملاحظات والتعليقات
- توثيق نقاط العمل

### 5. المتابعة والتقارير (Follow-up & Reports)
- متابعة تنفيذ القرارات
- تقارير حضور الاجتماعات
- إحصائيات الأداء
- تحليل فعالية الاجتماعات
- تصدير التقارير

## هيكل النماذج (Models Documentation)

### Meeting (الاجتماع)
```python
class Meeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'مجدول'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
        ('postponed', 'مؤجل'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'عام'),
        ('private', 'خاص'),
        ('confidential', 'سري'),
    ]
    
    title = models.CharField(max_length=200)                           # عنوان الاجتماع
    description = models.TextField()                                   # وصف الاجتماع
    objectives = models.TextField(blank=True)                          # أهداف الاجتماع
    
    # التوقيت والمكان
    start_datetime = models.DateTimeField()                            # تاريخ ووقت البداية
    end_datetime = models.DateTimeField()                              # تاريخ ووقت النهاية
    location = models.CharField(max_length=200)                        # المكان
    meeting_room = models.ForeignKey('MeetingRoom', on_delete=models.SET_NULL, null=True, blank=True) # قاعة الاجتماع
    
    # الحالة والخصوصية
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled') # الحالة
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public') # مستوى الخصوصية
    
    # المنظم والمشاركون
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings') # المنظم
    participants = models.ManyToManyField(User, through='MeetingParticipant', related_name='meetings') # المشاركون
    
    # الربط بالمشاريع والأقسام
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True) # المشروع
    department = models.ForeignKey('Hr.Department', on_delete=models.SET_NULL, null=True, blank=True) # القسم
    
    # معلومات إضافية
    is_recurring = models.BooleanField(default=False)                  # اجتماع متكرر
    recurrence_pattern = models.JSONField(null=True, blank=True)       # نمط التكرار
    parent_meeting = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True) # الاجتماع الأصل
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)                   # تاريخ التحديث
    
    class Meta:
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['start_datetime']),
            models.Index(fields=['status']),
            models.Index(fields=['organizer']),
        ]
```

### MeetingParticipant (مشارك الاجتماع)
```python
class MeetingParticipant(models.Model):
    ROLE_CHOICES = [
        ('organizer', 'منظم'),
        ('presenter', 'مقدم'),
        ('participant', 'مشارك'),
        ('observer', 'مراقب'),
        ('secretary', 'سكرتير'),
    ]
    
    RESPONSE_CHOICES = [
        ('pending', 'معلق'),
        ('accepted', 'مقبول'),
        ('declined', 'مرفوض'),
        ('tentative', 'مؤقت'),
    ]
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)     # الاجتماع
    user = models.ForeignKey(User, on_delete=models.CASCADE)           # المستخدم
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant') # الدور
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES, default='pending') # الرد
    is_required = models.BooleanField(default=True)                    # مطلوب الحضور
    attended = models.BooleanField(default=False)                      # حضر فعلياً
    invited_at = models.DateTimeField(auto_now_add=True)               # تاريخ الدعوة
    responded_at = models.DateTimeField(null=True, blank=True)         # تاريخ الرد
    notes = models.TextField(blank=True)                               # ملاحظات
    
    class Meta:
        unique_together = ['meeting', 'user']
```

### MeetingAgenda (جدول أعمال الاجتماع)
```python
class MeetingAgenda(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='agenda_items') # الاجتماع
    title = models.CharField(max_length=200)                           # عنوان البند
    description = models.TextField()                                   # وصف البند
    presenter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # المقدم
    estimated_duration = models.DurationField()                       # المدة المقدرة
    actual_duration = models.DurationField(null=True, blank=True)      # المدة الفعلية
    order = models.PositiveIntegerField(default=0)                     # الترتيب
    is_completed = models.BooleanField(default=False)                  # مكتمل
    notes = models.TextField(blank=True)                               # ملاحظات
    
    class Meta:
        ordering = ['order']
```

### MeetingMinutes (محضر الاجتماع)
```python
class MeetingMinutes(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name='minutes') # الاجتماع
    content = models.TextField()                                       # محتوى المحضر
    decisions = models.TextField(blank=True)                           # القرارات
    action_items = models.TextField(blank=True)                        # بنود العمل
    next_steps = models.TextField(blank=True)                          # الخطوات التالية
    
    # معلومات التوثيق
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # مسجل المحضر
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_minutes') # معتمد المحضر
    is_approved = models.BooleanField(default=False)                   # معتمد
    
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)                   # تاريخ التحديث
```

### MeetingRoom (قاعة الاجتماع)
```python
class MeetingRoom(models.Model):
    name = models.CharField(max_length=100)                            # اسم القاعة
    location = models.CharField(max_length=200)                        # الموقع
    capacity = models.PositiveIntegerField()                           # السعة
    equipment = models.JSONField(default=list)                         # المعدات المتاحة
    is_available = models.BooleanField(default=True)                   # متاحة
    booking_rules = models.TextField(blank=True)                       # قواعد الحجز
    
    def is_available_at(self, start_time, end_time, exclude_meeting=None):
        """فحص توفر القاعة في وقت محدد"""
        conflicts = Meeting.objects.filter(
            meeting_room=self,
            start_datetime__lt=end_time,
            end_datetime__gt=start_time,
            status__in=['scheduled', 'in_progress']
        )
        
        if exclude_meeting:
            conflicts = conflicts.exclude(id=exclude_meeting.id)
        
        return not conflicts.exists()
```

### MeetingAttachment (مرفق الاجتماع)
```python
class MeetingAttachment(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attachments') # الاجتماع
    title = models.CharField(max_length=200)                           # عنوان المرفق
    file = models.FileField(upload_to='meetings/attachments/')         # الملف
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)    # رافع الملف
    uploaded_at = models.DateTimeField(auto_now_add=True)              # تاريخ الرفع
    is_public = models.BooleanField(default=True)                      # عام للجميع
    description = models.TextField(blank=True)                         # وصف المرفق
```

## العروض (Views Documentation)

### عروض إدارة الاجتماعات (Meeting Management Views)

#### MeetingListView
```python
class MeetingListView(LoginRequiredMixin, ListView):
    """عرض قائمة الاجتماعات"""
    model = Meeting
    template_name = 'meetings/meeting_list.html'
    context_object_name = 'meetings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Meeting.objects.filter(
            Q(organizer=self.request.user) | 
            Q(participants=self.request.user)
        ).distinct()
        
        # فلترة حسب الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # فلترة حسب التاريخ
        date_filter = self.request.GET.get('date')
        if date_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(start_datetime__date=today)
        elif date_filter == 'week':
            week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
            week_end = week_start + timedelta(days=6)
            queryset = queryset.filter(start_datetime__date__range=[week_start, week_end])
        
        return queryset.order_by('-start_datetime')
```

#### MeetingCreateView
```python
class MeetingCreateView(LoginRequiredMixin, CreateView):
    """إنشاء اجتماع جديد"""
    model = Meeting
    form_class = MeetingForm
    template_name = 'meetings/meeting_form.html'
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)
        
        # إضافة المنظم كمشارك
        MeetingParticipant.objects.create(
            meeting=self.object,
            user=self.request.user,
            role='organizer',
            response='accepted',
            attended=True
        )
        
        # إرسال دعوات للمشاركين
        self.send_invitations()
        
        return response
    
    def send_invitations(self):
        """إرسال دعوات للمشاركين"""
        # منطق إرسال الدعوات
        pass
```

#### MeetingDetailView
```python
class MeetingDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل الاجتماع"""
    model = Meeting
    template_name = 'meetings/meeting_detail.html'
    context_object_name = 'meeting'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إضافة معلومات المشاركة
        try:
            participant = MeetingParticipant.objects.get(
                meeting=self.object,
                user=self.request.user
            )
            context['user_participation'] = participant
        except MeetingParticipant.DoesNotExist:
            context['user_participation'] = None
        
        # إضافة جدول الأعمال
        context['agenda_items'] = self.object.agenda_items.all()
        
        # إضافة المرفقات
        context['attachments'] = self.object.attachments.filter(
            Q(is_public=True) | Q(uploaded_by=self.request.user)
        )
        
        return context
```

### عروض المشاركة (Participation Views)

#### respond_to_invitation
```python
@login_required
def respond_to_invitation(request, meeting_id):
    """الرد على دعوة الاجتماع"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    try:
        participant = MeetingParticipant.objects.get(
            meeting=meeting,
            user=request.user
        )
    except MeetingParticipant.DoesNotExist:
        messages.error(request, 'لم يتم العثور على دعوة لهذا الاجتماع')
        return redirect('meetings:meeting_detail', pk=meeting_id)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        notes = request.POST.get('notes', '')
        
        if response in ['accepted', 'declined', 'tentative']:
            participant.response = response
            participant.notes = notes
            participant.responded_at = timezone.now()
            participant.save()
            
            messages.success(request, 'تم تسجيل ردك بنجاح')
        
        return redirect('meetings:meeting_detail', pk=meeting_id)
    
    return render(request, 'meetings/respond_invitation.html', {
        'meeting': meeting,
        'participant': participant
    })
```

## النماذج (Forms Documentation)

### MeetingForm
```python
class MeetingForm(forms.ModelForm):
    """نموذج إنشاء/تعديل الاجتماع"""
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='المشاركون'
    )
    
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'objectives', 'start_datetime', 
                 'end_datetime', 'location', 'meeting_room', 'privacy_level',
                 'project', 'department', 'is_recurring']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_room': forms.Select(attrs={'class': 'form-select'}),
            'privacy_level': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
```

### MeetingAgendaForm
```python
class MeetingAgendaForm(forms.ModelForm):
    """نموذج بند جدول الأعمال"""
    class Meta:
        model = MeetingAgenda
        fields = ['title', 'description', 'presenter', 'estimated_duration', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'presenter': forms.Select(attrs={'class': 'form-select'}),
            'estimated_duration': forms.TimeInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
```

---

**تم إنشاء هذا التوثيق في**: 2025-06-16  
**الإصدار**: 1.0  
**المطور**: فريق تطوير نظام الدولية
