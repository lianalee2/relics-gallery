let scale = 1;
const img = document.getElementById('mainImage');

function zoomIn() {
    if (!img) return;
    scale += 0.2;
    applyTransform();
}

function zoomOut() {
    if (!img) return;
    if (scale > 0.4) scale -= 0.2;
    applyTransform();
}

function resetZoom() {
    if (!img) return;
    scale = 1;
    applyTransform();
}

function applyTransform() {
    img.style.transform = `scale(${scale})`;
}

function changeMainImage(imageSrc, thumbnailElement) {
    const mainImage = document.getElementById('mainImage');
    if (!mainImage) return;
    
    // 更新主图
    mainImage.src = imageSrc;
    
    // 重置缩放
    scale = 1;
    applyTransform();
    
    // 更新缩略图选中状态
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    thumbnails.forEach(thumb => {
        thumb.classList.remove('thumbnail-active');
        thumb.style.borderColor = '#ddd';
    });
    if (thumbnailElement) {
        thumbnailElement.classList.add('thumbnail-active');
        thumbnailElement.style.borderColor = '#333';
    }
}

function toggleFullscreen() {
    const viewer = document.querySelector('.image-viewer');
    if (!viewer) return;
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else if (viewer.requestFullscreen) {
        viewer.requestFullscreen();
    }
}

// 搜索框功能增强
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-bar input[type="text"]');
    const searchForm = document.querySelector('.search-bar form');
    
    if (searchInput && searchForm) {
        // 确保按Enter键也能提交搜索（虽然表单默认支持，但我们可以增强体验）
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const searchTerm = this.value.trim();
                if (searchTerm) {
                    searchForm.submit();
                }
            }
        });
    }
});