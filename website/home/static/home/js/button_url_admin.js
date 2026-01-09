// Fallback for DOMContentLoaded in case wagtail:load doesn't fire
document.addEventListener("DOMContentLoaded", function() {
  function hideAddButtonIfNeeded() {
    //TODO: Need to verify that this code works properly if multiple buttons have been added to the page
    document.querySelectorAll('[data-contentpath="url"]').forEach(function(container) {
      container.querySelectorAll('[data-streamfield-stream-container]').forEach(function(streamContainer) {
        console.log(streamContainer); //TODO: Remove before submitting pull request

        //Check for element in streamContainer with attribute = [data-streamfield-child] and style is null (or style is not "display: none;")
        const elementsWithoutStyle = Array.from(streamContainer.childNodes).filter(el => el.hasAttribute('data-streamfield-child') && (!el.hasAttribute('style') || el.style.display !== 'none'));
        console.log(elementsWithoutStyle); //TODO: Remove before submitting pull request

        const elementsNotDataStreamfieldChild = Array.from(streamContainer.childNodes).filter(el => !el.hasAttribute('data-streamfield-child'));
        //If element found, then set all divs without [data-streamfield-child] attribute in streamContainer to have style="display: none;" and aria-hidden="true"
        if (elementsWithoutStyle.length > 0)
        {
          elementsNotDataStreamfieldChild.forEach((element) => {
            element.style.display = 'none';
            element.setAttribute('aria-hidden', 'true');
          });
        }
        else //Else set last div without [data-streamfield-child] attribute to have style="" and remove aria-hidden attribute
        {
          const lastElement = elementsNotDataStreamfieldChild[elementsNotDataStreamfieldChild.length - 1];
          lastElement.style.display = '';
          lastElement.removeAttribute('aria-hidden');
        }
      })
      console.log(container); //TODO: Remove before submitting pull request
    })
  }

  // Run on load
  hideAddButtonIfNeeded();

  //TODO: Identify the correct event(s) to associate the action to hide the add buttons for URLs of button components.
  //TODO: Figure out what event is fired when the trash can icon is clicked on a URL object.
  document.body.addEventListener('click', function(e) {
    setTimeout(hideAddButtonIfNeeded, 100); // Delay to allow DOM update
  });
});
