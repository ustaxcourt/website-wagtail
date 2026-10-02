class ImportExportBlockDefinition extends window.wagtailStreamField.blocks
    .StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );

        // const fileInput = document.getElementById(prefix + '-fileinput');
        // const textField = document.getElementById(prefix + '-text');
        // const textInitialHeight = textField.style.height
        // if (textField.style.maxHeight == '') { textField.style.maxHeight = '30em'; }
        // textField.style.overflowY = 'auto';

        // const readFile = (source, target) => {
        //     const reader = new FileReader();
        //     reader.addEventListener('load', (event) => {
        //         target.value = event.target.result;
        //         target.style.height = textInitialHeight;
        //         target.style.height = target.scrollHeight
        //             + parseFloat(getComputedStyle(target).paddingTop)
        //             + parseFloat(getComputedStyle(target).paddingBottom) + 'px';
        //     });
        //     reader.readAsText(source);
        // }

        // fileInput.addEventListener('change', (event) => {
        //     event.preventDefault();
        //     const input = fileInput.files[0];
        //     readFile(input, textField)
        //     fileInput.value = '';
        //     fileInput.blur();
        // });

        // textField.parentElement.addEventListener('dragover', (event) => {
        //     event.stopPropagation();
        //     event.preventDefault();
        //     event.dataTransfer.dropEffect = 'copy';
        // });
        // textField.parentElement.addEventListener('drop', (event) => {
        //     event.stopPropagation();
        //     event.preventDefault();
        //     const input = event.dataTransfer.files[0];
        //     readFile(input, textField)
        // });

        return block;
    }
}

window.telepath.register('blocks.models.ImportExportBlock', ImportExportBlockDefinition);
