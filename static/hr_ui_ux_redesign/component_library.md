# HR UI/UX Redesign - Component Library

This document describes the reusable UI components for the HR application redesign. All components are accessible, responsive, and follow Material Design principles.

## 1. Card
- `.card`: Container for content, with shadow, padding, and rounded corners.
- Usage: Employee profile, checklist item, review summary, etc.

## 2. Button
- `.btn`, `.btn-secondary`, `.btn-danger`, `.btn-success`: Primary, secondary, danger, and success actions.
- Accessible with keyboard and screen readers.

## 3. Form Group
- `.form-group`: Label + input/textarea/select, with spacing and focus states.
- Inputs: `<input>`, `<select>`, `<textarea>` styled for clarity and accessibility.

## 4. Table
- `.table`: Responsive, styled for payroll, reports, and lists.
- Use `<thead>`, `<tbody>`, `<th>`, `<td>` for semantic structure.

## 5. Grid
- `.grid`, `.grid-2`, `.grid-3`, `.grid-4`: Responsive grid layouts for arranging cards, forms, or lists.

## 6. Typography
- `.h1`, `.h2`, `.h3`, `.label`, `.text-muted`, `.text-success`, `.text-danger`, `.text-primary`.

## 7. Utility Classes
- `.mt-2`, `.mb-2`, `.mx-auto`, `.text-center`, `.fade-in` (animation), etc.

## 8. Accessibility
- All interactive elements have `aria-label` and proper focus states.
- Use `aria-live` for dynamic updates.

## 9. Example Usage
```html
<div class="container">
  <div class="grid grid-2">
    <div class="card">
      <h2 class="h2">Employee Profile</h2>
      <div class="form-group">
        <label for="empName">Name</label>
        <input id="empName" type="text" value="John Doe" />
      </div>
      <button class="btn">Save</button>
    </div>
    <div class="card">
      <h2 class="h2">Payroll Report</h2>
      <table class="table">
        <thead><tr><th>Month</th><th>Amount</th></tr></thead>
        <tbody><tr><td>May</td><td>$2000</td></tr></tbody>
      </table>
    </div>
  </div>
</div>
```

---

For more, see the HTML templates and `style.css`.
