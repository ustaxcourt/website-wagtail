# 17. NewsItem Snippet Date Field JavaScript Dependency

Date: 2025-08-15

## Status

Accepted

## Context

The NewsItem snippet in the Wagtail admin interface requires JavaScript functionality for its date input fields (`publish_date` and `homepage_display_expiration_date`). These fields use HTML5 date input widgets that depend on browser-native JavaScript functionality for date picker interactions and real-time date validation when users enter dates manually.

Key requirements:
- Date picker functionality in Wagtail admin for NewsItem creation/editing
- Provide real-time date validation and formatting as users type
- Ensure consistent date input behavior across different browsers
- Maintain compatibility with Wagtail's admin interface

## Decision

We rely on browser-native HTML5 date input functionality for NewsItem date fields, implemented through Django's `DateInput` widget with `type="date"` attributes.

### Implementation Details

**Field Panel Configuration** (`home/models/snippets/news_item.py:92-95`):
```python
panels = [
    # ... other fields
    FieldPanel("publish_date", classname="publish-date-picker"),
    FieldPanel("homepage_display_expiration_date", classname="expiration-date-picker"),
    # ... other fields
]
```

### Custom JavaScript Enhancement

**Automatic Expiration Date Setting** (`home/static/home/js/news_item_admin.js`):

In addition to browser-native date functionality, a custom JavaScript file provides automatic calculation of the `homepage_display_expiration_date` when users enter a `publish_date`.

**Script Integration** (`home/wagtail_hooks.py:117-121`):
```python
@hooks.register("insert_global_admin_js")
def global_admin_js():
    return format_html(
        '<script src="{}"></script>', static("home/js/news_item_admin.js")
    )
```

**Execution Controls and Safeguards**:

1. **Page-Specific Execution**: Script only runs on NewsItem admin pages
   ```javascript
   function shouldInitialize() {
     return window.location.href.includes('admin/snippets/home/newsitem');
   }
   ```

2. **Event-Based Initialization**: Listens for Wagtail-specific events
   ```javascript
   document.addEventListener("wagtail:load", function() {
     if (shouldInitialize()) {
       initializeNewsItemDateLogic();
     }
   });
   ```

3. **Fallback Mechanism**: DOMContentLoaded fallback with delay for reliability
   ```javascript
   document.addEventListener("DOMContentLoaded", function() {
     if (shouldInitialize()) {
       setTimeout(initializeNewsItemDateLogic, 1000);
     }
   });
   ```

4. **Robust Element Selection**: Multiple selector strategies to find date inputs
   - CSS class selectors (`.publish-date-picker`, `.expiration-date-picker`)
   - Data attribute selectors (`[data-field="publish_date"]`)
   - Name attribute selectors (`input[name="publish_date"]`)

5. **Date Format Validation**: Handles multiple date input formats
   - ISO datetime format (`2023-12-01T10:30:00`)
   - Space-separated format (`2023-12-01 10:30:00`)
   - Date-only format (`2023-12-01`)

6. **Error Prevention**: Validates parsed dates before calculation
   ```javascript
   if (!isNaN(publishDate.getTime())) {
     // Only proceed with valid dates
     publishDate.setDate(publishDate.getDate() + 7);
   }
   ```

### JavaScript Dependencies and Safeguards

#### Browser-Native JavaScript Functionality
The date fields depend on browser-native JavaScript implementations that provide:

1. **Date Picker Interface**: Interactive calendar widgets for date selection
2. **Input Validation**: Real-time validation as users type dates manually
3. **Format Enforcement**: Automatic formatting to YYYY-MM-DD format
4. **Accessibility**: Keyboard navigation and screen reader support

#### Built-in Safeguards and Error Handling

1. **Input Type Validation**:
   - Browser automatically validates date format (YYYY-MM-DD)
   - Invalid dates are rejected at the input level
   - Users cannot submit forms with malformed dates

2. **Graceful Degradation**:
   - Browsers without HTML5 date support fall back to text inputs
   - Server-side validation in Django ensures data integrity regardless of client-side behavior

3. **User Experience Safeguards**:
   - Visual indicators for invalid date entries
   - Automatic date format correction where supported
   - Clear date format hints in input placeholders


#### Error Handling Mechanisms

1. **Client-Side Validation**:
   - Browser prevents submission of invalid dates
   - Real-time feedback for date format errors
   - Visual styling for invalid input states

2. **Server-Side Validation**:
   - Django form validation ensures proper datetime objects
   - Timezone conversion handles edge cases
   - Database constraints prevent invalid data storage

3. **Fallback Behavior**:
   - Text input fallback maintains functionality
   - Server validation catches any client-side bypasses
   - User-friendly error messages guide corrections

## Consequences

### Positive Consequences

1. **Enhanced User Experience**: Automatic expiration date calculation reduces manual entry errors
2. **Consistent Date Behavior**: Standard browser date picker behavior with custom enhancements
3. **Accessibility Compliance**: Browser-native controls meet accessibility standards automatically
4. **Robust Error Handling**: Multiple fallback mechanisms and date format validation
5. **Page-Specific Loading**: JavaScript only loads and executes where needed
6. **Event-Driven Architecture**: Wagtail-aware event handling ensures proper integration

### Negative Consequences

1. **Custom JavaScript Maintenance**: Requires ongoing maintenance of custom date calculation logic
2. **Browser Dependency**: Functionality varies across different browsers and versions
3. **Complex Element Selection**: Multiple selector strategies needed for robustness
4. **Testing Complexity**: Need to test across multiple browser implementations and date formats
5. **Timing Dependencies**: Relies on Wagtail event timing and DOM readiness

### Risk Mitigation

1. **Server-Side Validation**: All date inputs are validated on the server regardless of client behavior
2. **Progressive Enhancement**: The form works with text inputs if date inputs aren't supported
3. **User Guidance**: Clear labels and help text guide users on expected date formats
4. **Error Feedback**: Both client and server provide clear error messages for invalid dates

## Alternatives Considered

1. **Custom JavaScript Date Picker Library**: Rejected due to maintenance overhead and bundle size increase
2. **Wagtail's Built-in Date Widgets**: Current implementation already uses these effectively
3. **Third-party Widget Libraries**: Rejected to maintain simplicity and reduce dependencies
4. **Plain Text Fields with Manual Validation**: Rejected due to poor user experience
