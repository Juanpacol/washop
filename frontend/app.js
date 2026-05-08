/**
 * WASHOPS Frontend
 * Demostración de Patrones de Diseño
 */

class WashopsApp {
    constructor() {
        this.currentStep = 1;
        this.selectedService = null;
        this.selectedExtras = [];
        this.init();
        this.loadServices();
    }

    init() {
        this.setupEventListeners();
        this.setupNavigation();
    }

    loadServices() {
        const services = JSON.parse(localStorage.getItem('washops_services')) || [];
        this.displayServices(services);
        this.updateKanban(services);
        this.updateRecentActivity(services);
        this.generateCustomers(services);
        this.generatePayments(services);
        this.generateReports(services);
    }

    generateReports(services) {
        if (services.length === 0) {
            this.displayEmptyReports();
            return;
        }

        // Actualizar métricas KPI
        const totalRevenue = services.reduce((sum, s) => sum + s.price, 0);
        const totalServices = services.length;
        const uniqueCustomers = new Set(services.map(s => s.customer)).size;
        const avgTime = services.length > 0 ? Math.floor(Math.random() * 60) + 20 : 0;

        document.getElementById('metricRevenue').textContent = `$${(totalRevenue / 1000000).toFixed(2)}M`;
        document.getElementById('metricServices').textContent = totalServices;
        document.getElementById('metricCustomers').textContent = uniqueCustomers;
        document.getElementById('metricTime').textContent = `${avgTime} min`;

        // Preparar datos por tipo de servicio
        const serviceBreakdown = {};
        services.forEach(s => {
            if (!serviceBreakdown[s.type]) {
                serviceBreakdown[s.type] = { count: 0, revenue: 0 };
            }
            serviceBreakdown[s.type].count += 1;
            serviceBreakdown[s.type].revenue += s.price;
        });

        // Dibujar gráficos
        this.drawRevenueChart(services);
        this.drawPieChart(serviceBreakdown);
        this.displayPerformanceTable(serviceBreakdown);
    }

    drawRevenueChart(services) {
        const canvas = document.getElementById('revenueChart');
        if (!canvas || services.length === 0) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        // Generar datos simulados por día
        const dailyData = {};
        for (let i = 1; i <= 28; i++) {
            dailyData[i] = { revenue: Math.random() * 500000 + 100000, count: Math.floor(Math.random() * 15) + 5 };
        }

        ctx.fillStyle = '#f5f5f5';
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = '#fff';
        ctx.fillRect(padding, padding, chartWidth, chartHeight);

        // Dibujar barras
        const days = Object.keys(dailyData).length;
        const barWidth = chartWidth / days;

        Object.entries(dailyData).forEach(([day, data], idx) => {
            const revScale = chartHeight / 600000;
            const countScale = chartHeight / 25;

            const barX = padding + idx * barWidth + barWidth / 4;
            const revHeight = Math.min(data.revenue * revScale, chartHeight);

            ctx.fillStyle = '#00bcd4';
            ctx.fillRect(barX, padding + chartHeight - revHeight, barWidth / 2, revHeight);
        });

        // Labels
        ctx.fillStyle = '#666';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        for (let i = 0; i < days; i += 4) {
            ctx.fillText(i + 1, padding + i * barWidth + barWidth / 2, height - 10);
        }
    }

    drawPieChart(serviceBreakdown) {
        const canvas = document.getElementById('pieChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 80;

        const colors = { BASIC: '#ff6b6b', FULL: '#4dabf7', PREMIUM: '#9c27b0', EXPRESS: '#00bcd4' };
        const services = Object.entries(serviceBreakdown);
        const total = services.reduce((sum, [_, data]) => sum + data.revenue, 0);

        let currentAngle = 0;
        const legendHTML = [];

        services.forEach(([type, data]) => {
            const sliceAngle = (data.revenue / total) * Math.PI * 2;
            const percentage = Math.round((data.revenue / total) * 100);

            ctx.fillStyle = colors[type];
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();

            legendHTML.push(`
                <div class="legend-item">
                    <div class="legend-color" style="background: ${colors[type]}"></div>
                    <span>${type}: ${percentage}% - $${(data.revenue / 1000000).toFixed(2)}M</span>
                </div>
            `);

            currentAngle += sliceAngle;
        });

        document.getElementById('pieLegend').innerHTML = legendHTML.join('');
    }

    displayPerformanceTable(serviceBreakdown) {
        const tbody = document.getElementById('performanceTableBody');
        tbody.innerHTML = '';

        const total = Object.values(serviceBreakdown).reduce((sum, data) => sum + data.revenue, 0);
        const colors = { BASIC: '#ff6b6b', FULL: '#4dabf7', PREMIUM: '#9c27b0', EXPRESS: '#00bcd4' };

        Object.entries(serviceBreakdown)
            .sort((a, b) => b[1].revenue - a[1].revenue)
            .forEach(([type, data]) => {
                const avgPrice = Math.round(data.revenue / data.count);
                const percentage = Math.round((data.revenue / total) * 100);
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td><span class="service-name">${type}</span></td>
                    <td>${data.count} services</td>
                    <td>$${(data.revenue / 1000000).toFixed(2)}M</td>
                    <td>$${avgPrice.toLocaleString()}</td>
                    <td>${Math.floor(Math.random() * 60) + 20} min</td>
                    <td>
                        <span class="revenue-share-bar" style="width: ${percentage * 2}px; background: ${colors[type]};"></span>
                        ${percentage}%
                    </td>
                `;
                tbody.appendChild(row);
            });
    }

    displayEmptyReports() {
        document.getElementById('metricRevenue').textContent = '$0';
        document.getElementById('metricServices').textContent = '0';
        document.getElementById('metricCustomers').textContent = '0';
        document.getElementById('metricTime').textContent = '0 min';
    }

    generatePayments(services) {
        const payments = services.map((service, index) => {
            const methods = ['Cash', 'Nequi', 'Debit', 'Credit'];
            const statuses = ['Confirmed', 'Confirmed', 'Confirmed', 'Pending', 'Failed'];
            const method = methods[Math.floor(Math.random() * methods.length)];
            const status = statuses[Math.floor(Math.random() * statuses.length)];

            return {
                id: `#TRX${String(10000 + index).slice(-4)}`,
                date: service.timestamp.split(' ')[0],
                time: service.timestamp.split(' ')[1],
                service: service.id,
                customer: service.customer,
                serviceType: service.type,
                method: method,
                amount: service.price,
                status: status,
            };
        });

        localStorage.setItem('washops_payments', JSON.stringify(payments));
        this.displayPayments(payments);
    }

    displayPayments(payments) {
        const tbody = document.getElementById('paymentsTableBody');
        tbody.innerHTML = '';

        payments.forEach(payment => {
            const row = document.createElement('tr');
            const statusClass = `status-${payment.status.toLowerCase()}`;
            const methodIcons = {
                'Cash': '💵',
                'Nequi': '📱',
                'Debit': '🏧',
                'Credit': '💳'
            };

            row.innerHTML = `
                <td class="trx-id">${payment.id}</td>
                <td>${payment.date} ${payment.time}</td>
                <td>
                    <div style="font-weight: 600;">${payment.service}</div>
                    <div style="color: #999; font-size: 11px;">${payment.customer}</div>
                </td>
                <td>
                    <div class="payment-method-badge">
                        <span class="payment-icon">${methodIcons[payment.method]}</span>
                        ${payment.method}
                    </div>
                </td>
                <td>$${payment.amount.toLocaleString()}</td>
                <td>
                    <span class="payment-status ${statusClass}">● ${payment.status}</span>
                </td>
                <td>
                    <div class="service-actions-cell">
                        <button class="action-btn">⋮</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        this.updatePaymentMetrics(payments);
    }

    updatePaymentMetrics(payments) {
        const totalRevenue = payments.reduce((sum, p) => sum + p.amount, 0);
        const confirmedCount = payments.filter(p => p.status === 'Confirmed').length;

        document.getElementById('totalRevenue').textContent = `$${(totalRevenue / 1000000).toFixed(2)}M`;
        document.getElementById('revenueSubtitle').textContent = `March 2026 · ${payments.length} transactions`;

        // Service Type breakdown
        const serviceBreakdown = {};
        payments.forEach(p => {
            serviceBreakdown[p.serviceType] = (serviceBreakdown[p.serviceType] || 0) + p.amount;
        });

        const chartContainer = document.getElementById('serviceTypeChart');
        chartContainer.innerHTML = '';
        const totalAmount = Object.values(serviceBreakdown).reduce((a, b) => a + b, 0);

        Object.entries(serviceBreakdown).forEach(([service, amount]) => {
            const percentage = (amount / totalAmount) * 100;
            chartContainer.innerHTML += `
                <div class="chart-item">
                    <div class="chart-label">${service}</div>
                    <div class="chart-bar">
                        <div class="chart-bar-fill" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        });

        // Payment methods
        const methodBreakdown = {};
        payments.forEach(p => {
            methodBreakdown[p.method] = (methodBreakdown[p.method] || 0) + 1;
        });

        const methodsList = document.getElementById('paymentMethodsList');
        methodsList.innerHTML = '';
        const icons = {
            'Cash': '💵',
            'Nequi': '📱',
            'Debit': '🏧',
            'Credit': '💳'
        };

        Object.entries(methodBreakdown).forEach(([method, count]) => {
            methodsList.innerHTML += `
                <div class="method-item">
                    <span class="method-icon">${icons[method]}</span>
                    ${method} <span style="margin-left: auto; color: #999;">${count}</span>
                </div>
            `;
        });
    }

    generateCustomers(services) {
        const customersMap = {};

        services.forEach(service => {
            if (!customersMap[service.customer]) {
                customersMap[service.customer] = {
                    name: service.customer,
                    plate: service.plate,
                    phone: this.generatePhone(),
                    email: this.generateEmail(service.customer),
                    vehicles: [service.plate],
                    servicesCount: 1,
                    totalSpent: service.price,
                    type: this.getCustomerType(),
                    timestamp: service.timestamp
                };
            } else {
                customersMap[service.customer].servicesCount += 1;
                customersMap[service.customer].totalSpent += service.price;
                if (!customersMap[service.customer].vehicles.includes(service.plate)) {
                    customersMap[service.customer].vehicles.push(service.plate);
                }
            }
        });

        const customers = Object.values(customersMap);
        localStorage.setItem('washops_customers', JSON.stringify(customers));
        this.displayCustomers(customers);
    }

    generatePhone() {
        const area = Math.floor(Math.random() * 900) + 100;
        const exchange = Math.floor(Math.random() * 900) + 100;
        const line = Math.floor(Math.random() * 9000) + 1000;
        return `(${area}) ${exchange}-${line}`;
    }

    generateEmail(name) {
        const [first, last] = name.toLowerCase().split(' ');
        const domains = ['email.com', 'mail.com', 'inbox.com'];
        const domain = domains[Math.floor(Math.random() * domains.length)];
        return `${first}.${last}@${domain}`;
    }

    getCustomerType() {
        const types = ['FREQUENT', 'CORPORATE', 'OCCASIONAL'];
        const weights = [0.35, 0.15, 0.50]; // 35% frequent, 15% corporate, 50% occasional
        const random = Math.random();
        let cumulative = 0;
        for (let i = 0; i < types.length; i++) {
            cumulative += weights[i];
            if (random <= cumulative) return types[i];
        }
        return 'OCCASIONAL';
    }

    displayCustomers(customers) {
        const grid = document.getElementById('customersGrid');
        grid.innerHTML = '';

        customers.forEach(customer => {
            const avatarClass = `avatar-${customer.type.toLowerCase()}`;
            const initials = customer.name.split(' ').map(n => n[0]).join('');
            const vehiclesHtml = customer.vehicles.map(v => `<span class="vehicle-badge">🚗 ${v}</span>`).join('');
            const totalSpentFormatted = (customer.totalSpent / 1000).toFixed(1);

            const card = document.createElement('div');
            card.className = 'customer-card';
            card.innerHTML = `
                <div class="customer-header">
                    <div class="customer-avatar ${avatarClass}">${initials}</div>
                    <div class="customer-info">
                        <div class="customer-name">${customer.name}</div>
                        <div class="customer-type">${customer.type}</div>
                    </div>
                </div>

                <div class="customer-contact">
                    <div class="contact-item">
                        <span class="contact-icon">📞</span>
                        <span>${customer.phone}</span>
                    </div>
                    <div class="contact-item">
                        <span class="contact-icon">📧</span>
                        <span>${customer.email}</span>
                    </div>
                </div>

                <div class="customer-vehicles">${vehiclesHtml}</div>

                <div class="customer-stats">
                    <div class="stat-item">
                        <div class="stat-number">${customer.servicesCount}</div>
                        <div class="stat-label">Services</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">$${totalSpentFormatted}M</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>

                <div class="customer-actions">
                    <button class="customer-btn">View History</button>
                    <button class="customer-btn primary">New Service</button>
                </div>
            `;
            grid.appendChild(card);
        });

        this.updateCustomerFilters(customers);
    }

    updateCustomerFilters(customers) {
        const filters = {
            'all': customers.length,
            'FREQUENT': customers.filter(c => c.type === 'FREQUENT').length,
            'CORPORATE': customers.filter(c => c.type === 'CORPORATE').length,
            'OCCASIONAL': customers.filter(c => c.type === 'OCCASIONAL').length,
        };

        document.querySelectorAll('.customers-filters .filter-btn').forEach(btn => {
            const filter = btn.dataset.filter;
            const count = filters[filter];
            btn.textContent = filter === 'all'
                ? `All (${count})`
                : `${filter.charAt(0) + filter.slice(1).toLowerCase()} (${count})`;
        });
    }

    displayServices(services) {
        const tbody = document.querySelector('.services-table tbody');
        tbody.innerHTML = '';

        services.forEach(service => {
            const row = document.createElement('tr');
            const badgeClass = service.state.toLowerCase();
            row.innerHTML = `
                <td class="service-id">${service.id}</td>
                <td class="service-plate">${service.plate}</td>
                <td>
                    <div class="service-customer">${service.customer}</div>
                    <div class="service-vehicle">${service.plate}</div>
                </td>
                <td><span class="badge" style="background: #e3f2fd; color: #1976d2;">${service.type}</span></td>
                <td><span class="badge ${badgeClass}">${service.state}</span></td>
                <td>$${service.price.toLocaleString()}</td>
                <td>${service.timestamp.split(' ')[1] || '00:00'}</td>
                <td>
                    <div class="service-actions-cell">
                        <button class="action-btn" title="Edit">✎</button>
                        <button class="action-btn" title="More">⋯</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        this.updateFilterCounts(services);
    }

    updateFilterCounts(services) {
        const filters = {
            'all': services.length,
            'PENDING': services.filter(s => s.state === 'PENDING').length,
            'IN_PROGRESS': services.filter(s => s.state === 'IN_PROGRESS').length,
            'COMPLETED': services.filter(s => s.state === 'COMPLETED').length,
            'CANCELLED': services.filter(s => s.state === 'CANCELLED').length,
        };

        document.querySelectorAll('.filter-btn').forEach(btn => {
            const filter = btn.dataset.filter;
            const count = filters[filter];
            btn.textContent = filter === 'all'
                ? `All (${count})`
                : `${filter.charAt(0) + filter.slice(1).toLowerCase()} (${count})`;
        });
    }

    updateKanban(services) {
        const pending = services.filter(s => s.state === 'PENDING');
        const inProgress = services.filter(s => s.state === 'IN_PROGRESS');
        const completed = services.filter(s => s.state === 'COMPLETED');

        this.populateKanbanColumn(0, pending, 'Pendiente');
        this.populateKanbanColumn(1, inProgress, 'En Progreso');
        this.populateKanbanColumn(2, completed, 'Completado');
    }

    populateKanbanColumn(columnIndex, services, label) {
        const columns = document.querySelectorAll('.kanban-column');
        const column = columns[columnIndex];
        const h3 = column.querySelector('h3');
        h3.textContent = `${label} (${services.length})`;

        const cards = column.querySelectorAll('.kanban-card');
        cards.forEach(card => card.remove());

        services.forEach(service => {
            const card = document.createElement('div');
            card.className = 'kanban-card';
            const badgeClass = service.state.toLowerCase();
            card.innerHTML = `
                <div class="card-id">${service.id}</div>
                <div class="card-plate">${service.plate}</div>
                <div class="card-service">${service.type}${service.extras.length > 0 ? ' + ' + service.extras.join(' + ') : ''}</div>
                <div class="card-price">$${service.price.toLocaleString()}</div>
                <span class="badge ${badgeClass}">${service.state}</span>
            `;
            column.appendChild(card);
        });
    }

    updateRecentActivity(services) {
        const activityList = document.getElementById('recentActivity');
        const sorted = [...services].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        const recent = sorted.slice(0, 5);

        activityList.innerHTML = '';

        if (recent.length === 0) {
            activityList.innerHTML = '<div class="activity-empty">Sin actividad</div>';
            return;
        }

        recent.forEach(service => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <div class="activity-text">
                    <span class="activity-icon">✓</span>
                    ${service.customer} - ${service.type}
                </div>
                <div style="font-size: 11px; color: #666; margin-top: 5px;">
                    ${new Date(service.timestamp).toLocaleString()}
                </div>
            `;
            activityList.appendChild(item);
        });
    }

    setupNavigation() {
        // Cambiar entre páginas
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const page = btn.dataset.page;
                this.navigateTo(page);
            });
        });
    }

    navigateTo(page) {
        // Ocultar todas las páginas
        document.querySelectorAll('.page-content').forEach(p => {
            p.classList.remove('active');
        });

        // Mostrar página seleccionada
        document.getElementById(page).classList.add('active');

        // Actualizar nav activo
        document.querySelectorAll('.nav-btn:not(.disabled-btn)').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.page === page) {
                btn.classList.add('active');
            }
        });

        // Actualizar título
        const titles = {
            dashboard: '🚿 Dashboard',
            services: '🚿 Services'
        };
        document.getElementById('pageTitle').textContent = titles[page];

        // Mostrar/ocultar botón nuevo servicio
        const btnNewService = document.getElementById('btnNewService');
        if (page === 'services') {
            btnNewService.style.display = 'block';
        } else {
            btnNewService.style.display = 'none';
        }
    }

    setupEventListeners() {
        // Botones para abrir modal
        document.getElementById('btnNewService').addEventListener('click', () => this.openModal());
        const btn2 = document.getElementById('btnNewService2');
        if (btn2) {
            btn2.addEventListener('click', () => this.openModal());
        }

        // Cerrar modal
        document.querySelector('.close-btn').addEventListener('click', () => this.closeModal());

        // PASO 1: Seleccionar tipo de servicio [FACTORY METHOD]
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', () => this.selectService(card));
        });

        // PASO 2: Seleccionar extras [DECORATOR PATTERN]
        document.querySelectorAll('.extra-checkbox input').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updatePrice());
        });

        // Navegación de pasos
        document.getElementById('btnNext').addEventListener('click', () => this.nextStep());
        document.getElementById('btnBack').addEventListener('click', () => this.prevStep());
        document.getElementById('btnCreate').addEventListener('click', () => this.createService());

        // Cerrar modal al hacer click afuera
        document.getElementById('modalNewService').addEventListener('click', (e) => {
            if (e.target.id === 'modalNewService') {
                this.closeModal();
            }
        });

        // Filtros de servicios
        document.querySelectorAll('.services-header .filter-btn').forEach(btn => {
            btn.addEventListener('click', () => this.filterServices(btn));
        });

        // Filtros de clientes
        document.querySelectorAll('.customers-filters .filter-btn').forEach(btn => {
            btn.addEventListener('click', () => this.filterCustomers(btn));
        });

        // Tabs de pagos
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn));
        });

        this.currentFilter = 'all';
    }

    switchTab(btn) {
        const tabName = btn.dataset.tab;

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        document.getElementById(`tab-${tabName}`).classList.add('active');
    }

    filterCustomers(btn) {
        document.querySelectorAll('.customers-filters .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const customers = JSON.parse(localStorage.getItem('washops_customers')) || [];
        const filterType = btn.dataset.filter;

        let filtered = customers;
        if (filterType !== 'all') {
            filtered = customers.filter(c => c.type === filterType);
        }

        this.displayCustomers(customers);
    }

    filterServices(btn) {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        this.currentFilter = btn.dataset.filter;
        const services = JSON.parse(localStorage.getItem('washops_services')) || [];

        let filtered = services;
        if (this.currentFilter !== 'all') {
            filtered = services.filter(s => s.state === this.currentFilter);
        }

        this.displayServices(services);
    }

    // PASO 1: FACTORY METHOD - Crear diferentes tipos de servicios
    selectService(card) {
        // Deseleccionar todos
        document.querySelectorAll('.service-card').forEach(c => {
            c.classList.remove('selected');
        });

        // Seleccionar este
        card.classList.add('selected');
        this.selectedService = {
            type: card.dataset.type,
            price: this.getPriceByType(card.dataset.type),
            name: card.querySelector('.service-name').textContent
        };

        this.updatePrice();
    }

    getPriceByType(type) {
        const prices = {
            'basic': 45000,
            'full': 75000,
            'premium': 120000,
            'express': 35000
        };
        return prices[type] || 0;
    }

    // PASO 2: DECORATOR PATTERN - Agregar extras
    updatePrice() {
        if (!this.selectedService) return;

        this.selectedExtras = [];
        let extrasTotal = 0;

        // Recolectar extras seleccionados
        document.querySelectorAll('.extra-checkbox input:checked').forEach(checkbox => {
            const name = checkbox.parentElement.querySelector('.extra-name').textContent;
            let price = 0;

            if (checkbox.value === 'waxing') {
                price = 15000;
                this.selectedExtras.push('Encerado');
            } else if (checkbox.value === 'vacuum') {
                price = 12000;
                this.selectedExtras.push('Vacío Interior');
            } else if (checkbox.value === 'tire') {
                price = 10000;
                this.selectedExtras.push('Pulimiento Llantas');
            }

            extrasTotal += price;
        });

        const total = this.selectedService.price + extrasTotal;

        // Actualizar UI
        document.getElementById('basePrice').textContent = `$${this.selectedService.price.toLocaleString()}`;
        document.getElementById('extrasPrice').textContent = `$${extrasTotal.toLocaleString()}`;
        document.getElementById('totalPrice').textContent = `$${total.toLocaleString()}`;
    }

    openModal() {
        document.getElementById('modalNewService').classList.add('active');
        this.currentStep = 1;
        this.showStep(1);
        this.selectedService = null;
        this.selectedExtras = [];
    }

    closeModal() {
        document.getElementById('modalNewService').classList.remove('active');
        this.resetForm();
    }

    resetForm() {
        document.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
        document.querySelectorAll('.extra-checkbox input').forEach(c => c.checked = false);
        document.getElementById('customerName').value = '';
        document.getElementById('vehiclePlate').value = '';
    }

    showStep(step) {
        // Ocultar todos los pasos
        document.querySelectorAll('.step').forEach(s => s.style.display = 'none');

        // Mostrar paso actual
        document.getElementById(`step${step}`).style.display = 'block';

        // Actualizar botones
        const btnBack = document.getElementById('btnBack');
        const btnNext = document.getElementById('btnNext');
        const btnCreate = document.getElementById('btnCreate');

        btnBack.style.display = step > 1 ? 'block' : 'none';
        btnNext.style.display = step < 3 ? 'block' : 'none';
        btnCreate.style.display = step === 3 ? 'block' : 'none';
    }

    nextStep() {
        if (this.currentStep === 1 && !this.selectedService) {
            alert('Por favor selecciona un tipo de servicio');
            return;
        }

        if (this.currentStep < 3) {
            this.currentStep++;
            this.showStep(this.currentStep);
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.showStep(this.currentStep);
        }
    }

    // PASO 3: STATE PATTERN - Crear servicio en estado PENDING
    createService() {
        const customerName = document.getElementById('customerName').value;
        const vehiclePlate = document.getElementById('vehiclePlate').value;

        if (!customerName || !vehiclePlate) {
            alert('Por favor completa todos los campos');
            return;
        }

        // Crear objeto de servicio (simulando lo que haría el backend)
        const newService = {
            id: `SV-${Math.floor(Math.random() * 10000)}`,
            type: this.selectedService.name,
            price: parseInt(document.getElementById('totalPrice').textContent.replace(/[^0-9]/g, '')),
            extras: this.selectedExtras,
            customer: customerName,
            plate: vehiclePlate,
            state: 'PENDING',  // STATE PATTERN: Estado inicial es PENDING
            timestamp: new Date().toLocaleString()
        };

        // Guardar en localStorage
        const services = JSON.parse(localStorage.getItem('washops_services')) || [];
        services.push(newService);
        localStorage.setItem('washops_services', JSON.stringify(services));

        console.log('Servicio creado y guardado:', newService);

        // Mostrar confirmación
        alert(
            `✓ Servicio creado exitosamente!\n\n` +
            `ID: ${newService.id}\n` +
            `Tipo: ${newService.type}\n` +
            `Cliente: ${customerName}\n` +
            `Placa: ${vehiclePlate}\n` +
            `Precio: $${newService.price.toLocaleString()}\n` +
            `Extras: ${newService.extras.length > 0 ? newService.extras.join(', ') : 'Ninguno'}\n` +
            `Estado: ${newService.state}`
        );

        // Actualizar tabla de servicios
        this.loadServices();
        this.closeModal();
    }
}

// Inicializar app cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WashopsApp();
    console.log('WASHOPS Frontend iniciado - Patrones de Diseño');
});
