// JavaScript Code for EasyICloud Application
const fileInput = document.getElementById('files');
const fileListDiv = document.getElementById('file-itemlist');
const folderNameInput = document.getElementById('folder_name');
const customPathInput = document.getElementById('custom_path');
const enableFolderCheckbox = document.getElementById('enable_folder_name');
const useCustomPathCheckbox = document.getElementById('use_custom_path');
const includeZipFilesCheckbox = document.getElementById('include_zip_files');
const filesArray = [];

// Toggle visibility of folder name input
function toggleFolderName() {
    folderNameInput.style.display = enableFolderCheckbox.checked ? 'block' : 'none';
}

// Toggle visibility of custom path input
function toggleCustomPath() {
    customPathInput.style.display = useCustomPathCheckbox.checked ? 'block' : 'none';
}

// Add files to the list when selected
fileInput.addEventListener('change', function() {
    const files = Array.from(fileInput.files);
    files.forEach(file => {
        if (!filesArray.includes(file.name)) {
            filesArray.push(file.name);
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            fileDiv.innerHTML = `
                <span class="file-name">${file.name}</span>
                <button type="button" class="btn-delete" onclick="removeFile(this, '${file.name}')">❌</button>
            `;
            fileListDiv.appendChild(fileDiv);
        }
    });
});

// Remove a file from the list
function removeFile(button, fileName) {
    const fileItem = button.parentElement;
    fileListDiv.removeChild(fileItem);
    const index = filesArray.indexOf(fileName);
    if (index > -1) {
        filesArray.splice(index, 1); 
    }
}

// Clear the entire selection
function clearSelection() {
    fileInput.value = '';
    fileListDiv.innerHTML = '';
    filesArray.length = 0;
}

document.getElementById('clear_selection').addEventListener('click', clearSelection);

// Submit files for merging
function submitFiles() {
    const formData = new FormData();

    if (fileInput.files.length === 0) {
        alert('Aucun fichier sélectionné.');
        return;
    }

    Array.from(fileInput.files).forEach(file => {
        formData.append('files', file);
    });

    formData.append('output_folder', enableFolderCheckbox.checked ? folderNameInput.value : '');
    formData.append('use_custom_path', useCustomPathCheckbox.checked);
    formData.append('custom_path', customPathInput.value);
    formData.append('include_zip_files', includeZipFilesCheckbox.checked);

    fetch('/merge', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') {
            clearSelection();
        }
    })
    .catch(error => {
        alert('Une erreur est survenue lors de l\'envoi des fichiers.');
    });
}