// Admin JavaScript - Funcionalidades principales

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    initTooltips();
    
    // Inicializar datatables
    initDataTables();
    
    // Configurar eventos
    setupEventListeners();
    
    // Cargar estadísticas
    loadStats();
});

// Tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'admin-tooltip';
            tooltip.textContent = this.title;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
        });
        
        el.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.admin-tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

// Tablas con funcionalidad extra
function initDataTables() {
    const tables = document.querySelectorAll('.crud-table, .dashboard-table');
    tables.forEach(table => {
        // Añadir ordenamiento por columna
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                sortTable(table, index);
            });
        });
        
        // Añadir paginación si hay muchas filas
        const rows = table.querySelectorAll('tbody tr');
        if (rows.length > 10) {
            addPagination(table);
        }
    });
}

// Ordenar tabla
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = table.dataset.sortColumn === columnIndex && table.dataset.sortOrder === 'asc';
    
    table.dataset.sortColumn = columnIndex;
    table.dataset.sortOrder = isAscending ? 'desc' : 'asc';
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Intentar convertir a número si es posible
        const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        return isAscending 
            ? aText.localeCompare(bText)
            : bText.localeCompare(aText);
    });
    
    // Limpiar y reinsertar filas
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    // Actualizar indicadores de ordenamiento
    updateSortIndicators(table, columnIndex, isAscending ? 'desc' : 'asc');
}

// Actualizar indicadores de ordenamiento
function updateSortIndicators(table, columnIndex, order) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.classList.remove('sort-asc', 'sort-desc');
        if (index === columnIndex) {
            header.classList.add(`sort-${order}`);
            header.innerHTML = header.textContent + 
                (order === 'asc' ? ' ↑' : ' ↓');
        }
    });
}

// Paginación para tablas grandes
function addPagination(table) {
    const rows = table.querySelectorAll('tbody tr');
    const pageSize = 10;
    let currentPage = 1;
    
    function showPage(page) {
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        
        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });
        
        updatePaginationControls();
    }
    
    function updatePaginationControls() {
        let controls = table.parentNode.querySelector('.table-pagination');
        if (!controls) {
            controls = document.createElement('div');
            controls.className = 'table-pagination';
            table.parentNode.appendChild(controls);
        }
        
        const totalPages = Math.ceil(rows.length / pageSize);
        controls.innerHTML = `
            <div class="pagination-info">
                Página ${currentPage} de ${totalPages} (${rows.length} registros)
            </div>
            <div class="pagination-buttons">
                <button class="btn-pagination prev" ${currentPage === 1 ? 'disabled' : ''}>
                    Anterior
                </button>
                ${Array.from({length: totalPages}, (_, i) => i + 1)
                    .map(page => `
                        <button class="btn-pagination ${page === currentPage ? 'active' : ''}">
                            ${page}
                        </button>
                    `).join('')}
                <button class="btn-pagination next" ${currentPage === totalPages ? 'disabled' : ''}>
                    Siguiente
                </button>
            </div>
        `;
        
        // Añadir event listeners
        controls.querySelectorAll('.btn-pagination').forEach(btn => {
            if (btn.classList.contains('prev')) {
                btn.addEventListener('click', () => {
                    if (currentPage > 1) {
                        currentPage--;
                        showPage(currentPage);
                    }
                });
            } else if (btn.classList.contains('next')) {
                btn.addEventListener('click', () => {
                    if (currentPage < totalPages) {
                        currentPage++;
                        showPage(currentPage);
                    }
                });
            } else if (!btn.classList.contains('active')) {
                btn.addEventListener('click', () => {
                    currentPage = parseInt(btn.textContent);
                    showPage(currentPage);
                });
            }
        });
    }
    
    // Mostrar primera página
    showPage(1);
}

// Configurar event listeners
function setupEventListeners() {
    // Cerrar mensajes de alerta
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.alert').remove();
        });
    });
    
    // Auto-ocultar mensajes después de 5 segundos
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
    
    // Confirmación para botones de eliminación
    document.querySelectorAll('.btn-delete, .btn-danger').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas continuar? Esta acción no se puede deshacer.')) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
    
    // Formularios con validación
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    isValid = false;
                    
                    // Mostrar mensaje de error
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'Este campo es requerido';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.style.display = 'block';
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.style.display = 'none';
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor completa todos los campos requeridos.');
            }
        });
    });
    
    // Menús desplegables
    document.querySelectorAll('.user-dropdown, .menu-item.has-children').forEach(dropdown => {
        const toggle = dropdown.querySelector('.user-toggle, > a');
        const menu = dropdown.querySelector('.user-menu, .dropdown');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            });
            
            // Cerrar al hacer clic fuera
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    menu.style.display = 'none';
                }
            });
        }
    });
    
    // === BÚSQUEDA CON DESACTIVACIÓN DE PAGINACIÓN ===
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase().trim();
            const table = document.querySelector('#dataTable');
            const rows = table ? table.querySelectorAll('tbody tr') : [];
            const pagination = document.querySelector('.pagination');
            
            // Mostrar/ocultar paginación
            if (searchTerm) {
                if (pagination) {
                    pagination.style.display = 'none';
                }
            } else {
                if (pagination) {
                    pagination.style.display = '';
                }
            }
            
            // Filtrar filas
            let visibleCount = 0;
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Mostrar mensaje si no hay resultados
            showNoResultsMessage(searchTerm, visibleCount);
        }, 300));
    }
    
    // Cambiar tamaño de página - VERIFICAR BÚSQUEDA ACTIVA
    const pageSizeSelect = document.getElementById('pageSize');
    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim()) {
                alert('No se puede cambiar el tamaño de página durante una búsqueda. Limpia la búsqueda primero.');
                this.value = this.dataset.previousValue || this.value;
                return;
            }
            
            // Guardar valor anterior
            this.dataset.previousValue = this.value;
            
            const size = this.value;
            const url = new URL(window.location);
            url.searchParams.set('page_size', size);
            url.searchParams.set('page', '1');
            window.location.href = url.toString();
        });
    }
    
    // Ordenar tabla - VERIFICAR BÚSQUEDA ACTIVA
    document.querySelectorAll('.crud-table th').forEach((th, index) => {
        th.addEventListener('click', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim()) {
                alert('No se puede ordenar la tabla durante una búsqueda. Limpia la búsqueda primero.');
                return;
            }
            
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isAscending = this.classList.contains('asc');
            this.classList.toggle('asc', !isAscending);
            this.classList.toggle('desc', isAscending);
            
            rows.sort((a, b) => {
                const aText = a.cells[index].textContent.trim();
                const bText = b.cells[index].textContent.trim();
                
                const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
                const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? aNum - bNum : bNum - aNum;
                }
                
                return isAscending 
                    ? aText.localeCompare(bText)
                    : bText.localeCompare(aText);
            });
            
            rows.forEach(row => tbody.appendChild(row));
        });
    });
    
    // Prevenir navegación por paginación si hay búsqueda
    document.querySelectorAll('.pagination a').forEach(link => {
        link.addEventListener('click', function(e) {
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim()) {
                e.preventDefault();
                alert('No se puede navegar por páginas durante una búsqueda. Limpia la búsqueda primero.');
                return false;
            }
        });
    });
    
    // Cambiar tema claro/oscuro
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('admin-theme', 
                document.body.classList.contains('dark-mode') ? 'dark' : 'light');
        });
        
        // Cargar tema guardado
        const savedTheme = localStorage.getItem('admin-theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        }
    }
}

// Mostrar mensaje de "no resultados"
function showNoResultsMessage(searchTerm, visibleCount) {
    if (!searchTerm || visibleCount > 0) {
        // Remover mensaje si existe
        const existingMessage = document.querySelector('.search-no-results');
        if (existingMessage) existingMessage.remove();
        return;
    }
    
    // Crear mensaje
    const message = document.createElement('div');
    message.className = 'search-no-results alert alert-warning';
    message.innerHTML = `
        <i class="fas fa-search"></i>
        No se encontraron resultados para "<strong>${searchTerm}</strong>"
        <button class="btn-clear-search" style="margin-left: 10px; padding: 2px 8px; font-size: 0.8em;">
            Limpiar búsqueda
        </button>
    `;
    
    // Insertar después de la tabla
    const tableContainer = document.querySelector('.table-responsive');
    if (tableContainer) {
        // Remover mensaje anterior
        const existingMessage = tableContainer.querySelector('.search-no-results');
        if (existingMessage) existingMessage.remove();
        
        tableContainer.appendChild(message);
        
        // Event listener para limpiar búsqueda
        message.querySelector('.btn-clear-search').addEventListener('click', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }
}

// Cargar estadísticas
function loadStats() {
    // En una implementación real, aquí harías una petición AJAX
    // Por ahora simulamos datos
    const stats = {
        totalSales: 12500,
        newOrders: 15,
        pendingTasks: 8,
        conversionRate: '4.2%'
    };
    
    // Actualizar elementos en el DOM
    Object.keys(stats).forEach(key => {
        const element = document.querySelector(`.stat-${key}`);
        if (element) {
            animateCounter(element, stats[key]);
        }
    });
}

// Animación de contadores
function animateCounter(element, targetValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = targetValue > currentValue ? 1 : -1;
    let current = currentValue;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = current;
        
        if (current === targetValue) {
            clearInterval(timer);
        }
    }, 50);
}

// Función debounce para búsqueda
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Notificaciones del sistema
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Animación de entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Cerrar notificación
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

// Gestión de archivos
function uploadFile(input, previewId) {
    const file = input.files[0];
    if (!file) return;
    
    const preview = document.getElementById(previewId);
    const reader = new FileReader();
    
    reader.onload = function(e) {
        preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
    };
    
    reader.readAsDataURL(file);
}

// Tema oscuro (estilos adicionales)
if (document.body.classList.contains('dark-mode')) {
    const darkModeStyles = `
        .dark-mode {
            --primary-color: #7b4b22;
            --primary-dark: #5b3a1a;
            --primary-light: #a16528;
            --light-color: #2d3748;
            --dark-color: #e2e8f0;
            --secondary-color: #a0aec0;
            background: #1a202c;
            color: #e2e8f0;
        }
        
        .dark-mode .admin-header {
            background: var(--primary-dark);
        }
        
        .dark-mode .admin-sidebar {
            background: #2d3748;
            border-right-color: #4a5568;
        }
        
        .dark-mode .admin-main {
            background: #1a202c;
        }
        
        .dark-mode .dashboard-section,
        .dark-mode .detail-section,
        .dark-mode .stat-card,
        .dark-mode .action-card,
        .dark-mode .option-card {
            background: #2d3748;
            color: #e2e8f0;
        }
        
        .dark-mode .table th,
        .dark-mode .table td {
            border-color: #4a5568;
        }
        
        .dark-mode input,
        .dark-mode select,
        .dark-mode textarea {
            background: #2d3748;
            color: #e2e8f0;
            border-color: #4a5568;
        }
        
        /* Estilos para búsqueda */
        .search-no-results {
            background: #4a5568 !important;
            border-color: #718096 !important;
            color: #e2e8f0 !important;
        }
    `;
    
    const style = document.createElement('style');
    style.textContent = darkModeStyles;
    document.head.appendChild(style);
}

// Estilos CSS para búsqueda (se añaden dinámicamente)
const searchStyles = `
    .search-no-results {
        background: #fff3cd !important;
        border: 1px solid #ffeaa7 !important;
        color: #856404 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin-top: 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    
    .search-no-results i {
        margin-right: 0.5rem;
    }
    
    .btn-clear-search {
        background: var(--warning) !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.3rem 0.8rem !important;
        font-size: 0.8rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .btn-clear-search:hover {
        background: #e0a800 !important;
        transform: translateY(-1px) !important;
    }
    
    .pagination[style*="display: none"] {
        opacity: 0.5;
        pointer-events: none;
        position: relative;
    }
    
    .pagination[style*="display: none"]::after {
        content: 'Búsqueda activa - Paginación deshabilitada';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--warning);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        z-index: 10;
        white-space: nowrap;
    }
`;

// Añadir estilos al documento
const styleTag = document.createElement('style');
styleTag.textContent = searchStyles;
document.head.appendChild(styleTag);