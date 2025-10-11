document.addEventListener('DOMContentLoaded', function() {
    // Episode inline form uchun
    const inlineForms = document.querySelectorAll('.inline-related');

    inlineForms.forEach(function(inline) {
        const fileInput = inline.querySelector('input[name$="-file"]');
        const videoUrlInput = inline.querySelector('input[name$="-video_url"]');
        const progressContainer = inline.querySelector('.field-file .fieldBox') || inline.querySelector('.field-file');

        if (fileInput && videoUrlInput) {
            // Progress bar yaratish
            const progressBar = document.createElement('progress');
            progressBar.style.width = '100%';
            progressBar.max = 100;
            progressBar.style.display = 'none';
            progressContainer.appendChild(progressBar);

            const statusText = document.createElement('span');
            statusText.style.marginLeft = '10px';
            progressContainer.appendChild(statusText);

            fileInput.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    statusText.textContent = 'Yuklanmoqda...';
                    progressBar.style.display = 'block';
                    progressBar.value = 0;

                    const formData = new FormData();
                    formData.append('file', file);

                    // CSRF token olish
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/upload-video/', true);
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);

                    xhr.upload.addEventListener('progress', function(e) {
                        if (e.lengthComputable) {
                            progressBar.value = (e.loaded / e.total) * 100;
                        }
                    });

                    xhr.addEventListener('load', function() {
                        if (xhr.status === 200) {
                            const response = JSON.parse(xhr.responseText);
                            videoUrlInput.value = response.video_url;
                            statusText.textContent = 'Yuklandi!';
                            progressBar.style.display = 'none';
                            fileInput.value = '';  // Fayl input ni tozalash
                        } else {
                            const response = JSON.parse(xhr.responseText);
                            statusText.textContent = 'Xatolik: ' + (response.error || 'Noma\'lum xatolik');
                            progressBar.style.display = 'none';
                        }
                    });

                    xhr.addEventListener('error', function() {
                        statusText.textContent = 'Yuklashda xatolik yuz berdi';
                        progressBar.style.display = 'none';
                    });

                    xhr.send(formData);
                }
            });
        }
    });
});
