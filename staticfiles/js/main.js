// ملف main.js

// 1. تحديث حالة المهمة ديناميكيًا
document.querySelectorAll('.change-status').forEach(function(button) {
    button.addEventListener('click', function() {
        var taskId = this.dataset.taskId;
        var newStatus = this.dataset.newStatus;
        fetch(`/tasks/${taskId}/update_status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify({status: newStatus})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`task-${taskId}-status`).textContent = newStatus === 'in_progress' ? 'يجرى العمل عليها' : newStatus;
                Toastify({
                    text: "تم تحديث حالة المهمة بنجاح!",
                    duration: 3000,
                    close: true,
                    gravity: "top",
                    position: "right",
                    backgroundColor: "#28a745",
                }).showToast();
            } else {
                alert('حدث خطأ أثناء تحديث الحالة');
            }
        });
    });
});

// 2. تأكيد الحذف
function confirmDelete(meetingId) {
    if (confirm("هل أنت متأكد من حذف هذا الاجتماع؟")) {
        window.location.href = `/meetings/delete/${meetingId}/`;
    }
}

// 3. إظهار رسائل Toast
function showToast(message, bgColor = "#28a745") {
    Toastify({
        text: message,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        backgroundColor: bgColor,
    }).showToast();
}