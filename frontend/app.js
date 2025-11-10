// frontend/app.js
const API = window.API_URL || "http://localhost:8000";

function notify(msg, timeout = 4000){
  const n = document.getElementById('notification');
  if (!n) return alert(msg);
  n.classList.remove('hidden');
  n.innerText = msg;
  setTimeout(()=> n.classList.add('hidden'), timeout);
}

async function post(path, body, useForm=false){
  const headers = useForm ? {} : {"Content-Type":"application/json"};
  const res = await fetch(API + path, {
    method: "POST",
    headers,
    body: useForm ? new URLSearchParams(body) : JSON.stringify(body)
  });
  return res;
}

function authHeader(){
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': 'Bearer ' + token } : {};
}

// Index (login/signup)
if (document.getElementById('login')){
  document.getElementById('login').onsubmit = async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const res = await post('/auth/login', {username, password, grant_type: 'password'}, true);
    if (res.ok){
      const j = await res.json();
      localStorage.setItem('access_token', j.access_token);
      notify('Login successful');
      window.location = 'dashboard.html';
    } else {
      const err = await res.json().catch(()=>({detail:'Login failed'}));
      notify('Login failed: ' + (err.detail || 'unknown'));
    }
  };

  document.getElementById('signup')?.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const fullName = document.getElementById('signupFullName').value;
    const password = document.getElementById('signupPassword').value;
    const res = await post('/auth/signup', {username, email, full_name: fullName, password});
    if (res.ok){
      notify('Account created — please login');
      document.getElementById('showLogin')?.click();
    } else {
      const err = await res.json().catch(()=>({detail:'Signup failed'}));
      notify('Signup failed: ' + (err.detail || 'unknown'));
    }
  });
}

// Dashboard logic
if (document.body.classList.contains('dashboard') || document.getElementById('profileView')){
  async function loadProfile(){
    const res = await fetch(API + '/users/me', { headers: authHeader() });
    if (res.ok){
      const user = await res.json();
      document.getElementById('profileUsername').value = user.username;
      document.getElementById('profileEmail').value = user.email || '';
      document.getElementById('profileFullName').value = user.full_name || '';
      document.getElementById('userInfo').innerText = `${user.username} (${user.role})`;
      if (user.role !== 'admin') document.querySelectorAll('.admin-only').forEach(el=>el.classList.add('hidden'));
    } else {
      notify('Not authorized');
      setTimeout(()=> window.location='index.html', 800);
    }
  }

  document.getElementById('logoutBtn')?.addEventListener('click', ()=>{
    localStorage.removeItem('access_token');
    window.location = 'index.html';
  });

  document.getElementById('profileForm')?.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const body = {
      full_name: document.getElementById('profileFullName').value,
      email: document.getElementById('profileEmail').value,
      current_password: document.getElementById('currentPassword').value || undefined,
      new_password: document.getElementById('newPassword').value || undefined
    };
    const res = await fetch(API + '/users/me', { method: 'PUT', headers: {...authHeader(), 'Content-Type':'application/json'}, body: JSON.stringify(body) });
    if (res.ok){
      notify('Profile updated');
      loadProfile();
    } else {
      const err = await res.json().catch(()=>({detail:'Update failed'}));
      notify('Update failed: ' + (err.detail || 'unknown'));
    }
  });

  // Admin pages
  async function loadUsers(){
    const res = await fetch(API + '/admin/users', { headers: authHeader() });
    if (res.ok){
      const users = await res.json();
      const tbody = document.querySelector('#usersTable tbody');
      tbody.innerHTML = '';
      users.forEach(u=>{
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${u.username}</td><td>${u.email}</td><td>${u.full_name||''}</td><td>${u.role}</td><td>${u.is_active? 'active':'inactive'}</td><td>${u.last_login||''}</td>`;
        tbody.appendChild(tr);
      });
    }
  }

  async function loadLogs(){
    const res = await fetch(API + '/admin/logs', { headers: authHeader() });
    if (res.ok){
      const logs = await res.json();
      const tbody = document.querySelector('#logsTable tbody');
      tbody.innerHTML = '';
      logs.forEach(l=>{
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(l.timestamp).toLocaleString()}</td><td>${l.username||''}</td><td>${l.action}</td><td>${l.ip_address||''}</td><td>${l.status}</td><td>${JSON.stringify(l.details||{})}</td>`;
        tbody.appendChild(tr);
      });
    }
  }

  // Navigation
  document.querySelectorAll('[data-view]').forEach(a=>{
    a.addEventListener('click', (e)=>{
      e.preventDefault();
      document.querySelectorAll('.dashboard-view').forEach(v=>v.classList.add('hidden'));
      document.querySelectorAll('.sidebar a').forEach(x=>x.classList.remove('active'));
      const view = a.getAttribute('data-view');
      document.getElementById(view + 'View').classList.remove('hidden');
      a.classList.add('active');
      if (view === 'users') loadUsers();
      if (view === 'logs') loadLogs();
    });
  });

  loadProfile();
}
