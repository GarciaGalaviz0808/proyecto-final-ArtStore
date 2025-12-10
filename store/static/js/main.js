// Menú hamburguesa responsive
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.querySelector('.menu-hamburguesa');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuBtn) {
        menuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Submenús en móviles
    const submenuItems = document.querySelectorAll('.submenu > a');
    submenuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                this.parentElement.classList.toggle('active');
            }
        });
    });
    
    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar') && window.innerWidth <= 768) {
            navLinks.classList.remove('active');
            document.querySelectorAll('.submenu').forEach(submenu => {
                submenu.classList.remove('active');
            });
        }
    });
    
    // Animación de métodos de pago
    const metodoPagoSelect = document.getElementById('metodo-pago');
    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener('change', function() {
            const animacion = document.getElementById('pago-animacion');
            if (animacion) {
                animacion.style.display = 'block';
                setTimeout(() => {
                    animacion.style.display = 'none';
                }, 2000);
            }
        });
    }
    
    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#f44336';
                    valid = false;
                } else {
                    field.style.borderColor = '#ccc';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Por favor completa todos los campos requeridos.');
            }
        });
    });
});