document.addEventListener('DOMContentLoaded', function() {
    // 设置默认日期为当前月份
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    document.getElementById('date').value = `${year}-${month}`;
    
    // 表单提交事件
    const indexForm = document.getElementById('indexForm');
    indexForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(indexForm);
        
        fetch('/add_record', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // 未认证，重定向到登录页面
                    window.location.href = '/login';
                    throw new Error('请先登录');
                }
                throw new Error('网络请求失败');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                updateUI(data);
                showSuccessMessage('数据已保存！');
            } else {
                showErrorMessage(data.message || '保存失败！');
            }
        })
        .catch(error => {
            console.error('错误:', error);
            showErrorMessage(error.message || '保存数据时出错，请重试！');
        });
    });
    
    // 刷新数据按钮
    document.getElementById('refreshData').addEventListener('click', function() {
        loadData();
    });
    
    // 页面加载时加载数据
    loadData();
    
    // 加载数据函数
    function loadData() {
        fetch('/get_data', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401) {
                        // 未认证，重定向到登录页面
                        window.location.href = '/login';
                        throw new Error('请先登录');
                    }
                    throw new Error('网络请求失败');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    updateUI(data);
                } else {
                    showErrorMessage(data.message || '获取数据失败！');
                }
            })
            .catch(error => {
                console.error('错误:', error);
                showErrorMessage(error.message || '加载数据时出错，请刷新页面！');
            });
    }
    
    // 更新UI函数
    function updateUI(data) {
        // 更新表格
        updateTable(data.data);
        
        // 更新图表
        updateChart(data.chart);
    }
    
    // 更新表格函数
    function updateTable(records) {
        const tableBody = document.getElementById('dataTable');
        const noDataRow = document.getElementById('noDataRow');
        
        // 清空表格内容
        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }
        
        if (records.length === 0) {
            // 如果没有数据，显示提示行
            tableBody.appendChild(noDataRow);
        } else {
            // 按日期降序排序
            records.sort((a, b) => b.date.localeCompare(a.date));
            
            // 填充表格数据
            records.forEach(record => {
                const row = document.createElement('tr');
                
                // 设置行内容
                row.innerHTML = `
                    <td>${record.date}</td>
                    <td>${record.salary.toFixed(2)}</td>
                    <td>${record.living_cost.toFixed(2)}</td>
                    <td class="${getIndexClass(record.index)}">${record.index.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-danger btn-sm delete-btn" data-date="${record.date}">删除</button>
                    </td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // 添加删除按钮事件
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const date = this.getAttribute('data-date');
                    if (confirm(`确定要删除 ${date} 的记录吗？`)) {
                        deleteRecord(date);
                    }
                });
            });
        }
    }
    
    // 更新图表函数
    function updateChart(chartData) {
        const chartImage = document.getElementById('chartImage');
        const chartPlaceholder = document.querySelector('.chart-placeholder');
        const downloadContainer = document.getElementById('chartDownloadContainer');
        const downloadButton = document.getElementById('downloadChart');
        
        // 移除之前的事件监听器以避免重复添加
        downloadButton.replaceWith(downloadButton.cloneNode(true));
        
        if (chartData) {
            chartImage.src = 'data:image/png;base64,' + chartData;
            chartImage.classList.remove('d-none');
            chartPlaceholder.classList.add('d-none');
            downloadContainer.classList.remove('d-none');
            
            // 重新获取按钮引用并添加下载功能
            document.getElementById('downloadChart').addEventListener('click', function() {
                // 创建一个临时链接来下载图片
                const link = document.createElement('a');
                link.href = chartImage.src;
                link.download = '独秀指数趋势图_' + new Date().toISOString().slice(0, 10) + '.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        } else {
            chartImage.classList.add('d-none');
            chartPlaceholder.classList.remove('d-none');
            downloadContainer.classList.add('d-none');
        }
    }
    
    // 删除记录函数
    function deleteRecord(date) {
        const formData = new FormData();
        formData.append('date', date);
        
        fetch('/delete_record', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // 未认证，重定向到登录页面
                    window.location.href = '/login';
                    throw new Error('请先登录');
                }
                throw new Error('网络请求失败');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                updateUI(data);
                showSuccessMessage('记录已删除！');
            } else {
                showErrorMessage(data.message || '删除失败！');
            }
        })
        .catch(error => {
            console.error('错误:', error);
            showErrorMessage(error.message || '删除记录时出错，请重试！');
        });
    }
    
    // 根据指数值获取样式类
    function getIndexClass(index) {
        if (index >= 2) return 'index-good';
        if (index >= 1) return 'index-medium';
        return 'index-poor';
    }
    
    // 显示成功消息
    function showSuccessMessage(message) {
        // 创建Toast消息
        showToast(message, 'success');
    }
    
    // 显示错误消息
    function showErrorMessage(message) {
        // 创建Toast消息
        showToast(message, 'danger');
    }
    
    // 显示Toast消息
    function showToast(message, type = 'primary') {
        // 检查是否已存在toast容器
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // 创建toast元素
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        // 初始化toast
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();
        
        // 监听隐藏事件以移除DOM元素
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    }
});
