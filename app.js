let agentData = [];
let taskData = [];
let historyData = [];
let currentAgentIdx = -1;
let currentTaskIdx = -1;

const API_BASE = 'http://127.0.0.1:5000';

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.textContent = `${icon} ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

function render() {
    document.getElementById('agent-count').textContent = agentData.length;
    document.getElementById('task-count').textContent = taskData.length;
    document.getElementById('history-count').textContent = historyData.length;
    
    let agentHtml = '';
    agentData.forEach((a, i) => {
        agentHtml += `<div class="card" data-agent="${i}">
            <div class="card-title">${a.name}</div>
            <div class="card-field">角色: ${a.role.substring(0, 30)}...</div>
            <div class="card-field">目标: ${a.goal.substring(0, 30)}...</div>
        </div>`;
    });
    document.getElementById('agent-list').innerHTML = agentHtml;
    
    let taskHtml = '';
    taskData.forEach((t, i) => {
        taskHtml += `<div class="card" data-task="${i}">
            <div class="card-title">${t.name}</div>
            <div class="card-field">描述: ${t.description.substring(0, 40)}...</div>
        </div>`;
    });
    document.getElementById('task-list').innerHTML = taskHtml;
    
    let historyHtml = '';
    if (historyData.length === 0) {
        historyHtml = '<div style="text-align:center;color:#888;">暂无调研记录</div>';
    } else {
        historyData.slice().reverse().forEach((h, i) => {
            const agentsList = h.agents ? h.agents.map(a => `<div style="margin-left:16px;">• ${a}</div>`).join('') : '';
            historyHtml += `<div class="history-item" data-history="${i}">
                <div class="history-header">
                    <span class="history-topic">${h.topic}</span>
                    <span class="history-time">${h.timestamp}</span>
                </div>
                <div class="history-detail" id="history-detail-${i}">
                    <div class="card-field">Agent团队:</div>${agentsList}
                    <div class="card-field" style="margin-top:12px;">调研结果:</div>
                    <div style="white-space:pre-wrap;margin-top:8px;">${h.result ? h.result.substring(0, 500) : ''}</div>
                </div>
            </div>`;
        });
    }
    document.getElementById('history-list').innerHTML = historyHtml;
}

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('dashboard-page').style.display = btn.dataset.page === 'dashboard' ? 'block' : 'none';
        document.getElementById('new-page').style.display = btn.dataset.page === 'new' ? 'block' : 'none';
        document.getElementById('history-page').style.display = btn.dataset.page === 'history' ? 'block' : 'none';
    });
});

document.getElementById('agent-list').addEventListener('click', e => {
    const card = e.target.closest('.card[data-agent]');
    if (card) {
        currentAgentIdx = parseInt(card.dataset.agent);
        const a = agentData[currentAgentIdx];
        document.getElementById('agent-name').value = a.name;
        document.getElementById('agent-role').value = a.role;
        document.getElementById('agent-goal').value = a.goal;
        document.getElementById('agent-backstory').value = a.backstory;
        document.getElementById('agent-tools').checked = a.tools;
        document.getElementById('agent-modal').classList.add('active');
    }
});

document.getElementById('task-list').addEventListener('click', e => {
    const card = e.target.closest('.card[data-task]');
    if (card) {
        currentTaskIdx = parseInt(card.dataset.task);
        const t = taskData[currentTaskIdx];
        document.getElementById('task-name').value = t.name;
        document.getElementById('task-desc').value = t.description;
        document.getElementById('task-output').value = t.expected_output;
        document.getElementById('task-modal').classList.add('active');
    }
});

document.getElementById('history-list').addEventListener('click', e => {
    const item = e.target.closest('.history-item');
    if (item) {
        const idx = parseInt(item.dataset.history);
        const detail = document.getElementById('history-detail-' + idx);
        if (detail) detail.classList.toggle('open');
    }
});

document.getElementById('close-agent').onclick = () => { 
    document.getElementById('agent-modal').classList.remove('active'); 
    currentAgentIdx = -1; 
};
document.getElementById('close-task').onclick = () => { 
    document.getElementById('task-modal').classList.remove('active'); 
    currentTaskIdx = -1; 
};

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', e => {
        if (e.target === modal) {
            modal.classList.remove('active');
            currentAgentIdx = -1;
            currentTaskIdx = -1;
        }
    });
});

document.getElementById('save-agent').onclick = async () => {
    if (currentAgentIdx >= 0) {
        agentData[currentAgentIdx] = {
            name: document.getElementById('agent-name').value,
            role: document.getElementById('agent-role').value,
            goal: document.getElementById('agent-goal').value,
            backstory: document.getElementById('agent-backstory').value,
            tools: document.getElementById('agent-tools').checked
        };
        render();
        document.getElementById('agent-modal').classList.remove('active');
        showToast('Agent 保存成功');
        
        try {
            await fetch(`${API_BASE}/api/agent`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: currentAgentIdx, data: agentData[currentAgentIdx] })
            });
        } catch(e) { 
            console.error(e); 
            showToast('保存失败', 'error');
        }
    }
};

document.getElementById('save-task').onclick = async () => {
    if (currentTaskIdx >= 0) {
        taskData[currentTaskIdx] = {
            name: document.getElementById('task-name').value,
            description: document.getElementById('task-desc').value,
            expected_output: document.getElementById('task-output').value
        };
        render();
        document.getElementById('task-modal').classList.remove('active');
        showToast('Task 保存成功');
        
        try {
            await fetch(`${API_BASE}/api/task`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: currentTaskIdx, data: taskData[currentTaskIdx] })
            });
        } catch(e) { 
            console.error(e); 
            showToast('保存失败', 'error');
        }
    }
};

document.getElementById('start-btn').onclick = async () => {
    const btn = document.getElementById('start-btn');
    const topic = document.getElementById('topic-input').value.trim();
    
    if (btn.classList.contains('running')) {
        btn.classList.remove('running');
        btn.textContent = '开始调研';
        document.getElementById('spinner').classList.remove('active');
        showToast('已停止调研', 'info');
        return;
    }
    
    if (!topic) { showToast('请输入调研主题', 'error'); return; }
    
    btn.classList.add('running');
    btn.textContent = '停止调研';
    document.getElementById('spinner').classList.add('active');
    document.getElementById('result-area').innerHTML = '';
    
    try {
        const res = await fetch(`${API_BASE}/api/research`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });
        const data = await res.json();
        document.getElementById('spinner').classList.remove('active');
        btn.classList.remove('running');
        btn.textContent = '开始调研';
        
        if (data.success) {
            document.getElementById('result-area').innerHTML = `<div class="success">✅ 调研完成！</div><div class="result-box">${(data.result || '').substring(0, 5000)}</div>`;
            historyData = data.history || [];
            render();
        } else {
            document.getElementById('result-area').innerHTML = `<div class="error">❌ 执行失败: ${data.error || ''}</div>`;
        }
    } catch(e) {
        document.getElementById('spinner').classList.remove('active');
        btn.classList.remove('running');
        btn.textContent = '开始调研';
        document.getElementById('result-area').innerHTML = `<div class="error">❌ 请求失败: ${e.message}</div>`;
    }
};

async function loadData() {
    try {
        const res = await fetch(`${API_BASE}/api/data`);
        const data = await res.json();
        agentData = data.agents || [];
        taskData = data.tasks || [];
        historyData = data.history || [];
        render();
    } catch(e) {
        console.error('Failed to load data:', e);
    }
}

loadData();
