const API = "http://localhost:3000/api";

let currentUser = JSON.parse(localStorage.getItem("user") || "null");
function saveUser(u){ localStorage.setItem("user", JSON.stringify(u)); currentUser = u; renderSession(); }

const qs = (s,root=document)=>root.querySelector(s);
const qsa = (s,root=document)=>[...root.querySelectorAll(s)];
function toast(msg, type="ok"){
  const wrap = qs("#toast-wrap");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(()=> el.remove(), 3500);
}
async function api(path, { method="GET", headers={}, body=null } = {}){
  const opts = { method, headers: { "Content-Type":"application/json", ...headers } };
  if(body !== null) opts.body = typeof body === "string" ? body : JSON.stringify(body);
  let res,text; try{ res=await fetch(`${API}${path}`,opts); text=await res.text(); }catch(e){ return { ok:false, data:{ ok:false, msg:String(e) } }; }
  let json; try{ json=text?JSON.parse(text):{}; }catch{ json={ ok:false, msg:"Respuesta no-JSON", raw:text?.slice(0,200) }; }
  return { ok: res.ok && (json.ok!==false || json.ok===undefined), status:res.status, data:json };
}

const views = { market:qs("#view-market"), access:qs("#view-access"), admin:qs("#view-admin"), about:qs("#view-about") };
function show(v){ Object.values(views).forEach(x=>x.classList.remove("active")); views[v].classList.add("active");
  if(v==="market") loadPlans(); if(v==="access") loadPurchases(); if(v==="about") loadSOA();
}
qsa(".nav-btn").forEach(b=> b.addEventListener("click", ()=> show(b.dataset.view)));

function renderSession(){
  const who=qs("#whoami"), login=qs("#btnLogin"), logout=qs("#btnLogout"), adminEls=qsa(".admin-only");
  if(currentUser){ who.textContent=`${currentUser.name} (${currentUser.role})`; login.classList.add("hidden"); logout.classList.remove("hidden");
    if(currentUser.role==="admin") adminEls.forEach(e=>e.classList.remove("hidden")); else adminEls.forEach(e=>e.classList.add("hidden"));
  }else{ who.textContent="No autenticado"; login.classList.remove("hidden"); logout.classList.add("hidden"); adminEls.forEach(e=>e.classList.add("hidden")); }
}
renderSession();

const modal=qs("#modal");
qs("#btnLogin").onclick=()=>modal.classList.remove("hidden");
qs("#closeModal").onclick=()=>modal.classList.add("hidden");
qsa(".tab").forEach(t=>{ t.onclick=()=>{ qsa(".tab").forEach(x=>x.classList.remove("active")); qsa(".pane").forEach(x=>x.classList.remove("active"));
  t.classList.add("active"); qs(`#pane-${t.dataset.tab}`).classList.add("active"); }; });

qs("#form-login").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const email=qs("#l-email").value.trim(), password=qs("#l-pass").value.trim();
  const r=await api("/login",{ method:"POST", body:{ email,password } });
  if(!r.ok){ toast(r.data?.msg||"Error login","err"); return; }
  saveUser(r.data.user); modal.classList.add("hidden"); toast(`Hola, ${r.data.user.name}`); show("market");
});
qs("#form-register").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const name=qs("#r-name").value.trim(), email=qs("#r-email").value.trim(), password=qs("#r-pass").value.trim();
  const r=await api("/register",{ method:"POST", body:{ name,email,password } });
  if(!r.ok){ toast(r.data?.msg||"Error registro","err"); return; }
  toast("Cuenta creada. Entra con tu correo y password.");
});
qs("#btnLogout").onclick=()=>{ localStorage.removeItem("user"); currentUser=null; renderSession(); toast("Sesión cerrada"); };

let currentPlans=[];
function renderPlans(list){
  const wrap=qs("#plans");
  if(!list.length){ wrap.innerHTML="<div class='muted'>No hay planes publicados aún.</div>"; return; }
  wrap.innerHTML=""; list.forEach(p=>{
    const el=document.createElement("div"); el.className="card";
    el.innerHTML=`
      <div class="row" style="justify-content:space-between;align-items:center"><h3>${p.name}</h3><span class="badge">Proveedor: Empresa A</span></div>
      <p class="muted">${p.description||"Sin descripción"}</p>
      <div class="item"><span class="price">$${Number(p.price).toFixed(2)}</span><button class="btn" data-id="${p.id}" data-price="${p.price}">Comprar</button></div>`;
    wrap.appendChild(el);
  });
  qsa("button.btn[data-id]",wrap).forEach(btn=>{
    btn.onclick=async()=>{
      if(!currentUser){ toast("Inicia sesión para comprar.","err"); return; }
      const planId=btn.dataset.id, price=Number(btn.dataset.price);
      const r=await api("/purchase",{ method:"POST", body:{ userId:currentUser.id, planId, priceSnapshot:price } });
      if(!r.ok){ toast(r.data?.msg||"No se pudo comprar","err"); return; }
      toast(`Compra OK. Código: ${r.data.purchase.code}`); show("access"); loadPurchases();
    };
  });
}
async function loadPlans(){
  const wrap=qs("#plans"); wrap.innerHTML=`<div class="row"><div class="loader"></div><span class="muted">Cargando planes...</span></div>`;
  const r=await api("/plans"); if(!r.ok){ wrap.innerHTML="<div class='muted'>Error cargando planes</div>"; return; }
  currentPlans=r.data?.plans||[]; const q=qs("#plan-search").value.toLowerCase().trim();
  renderPlans(q?currentPlans.filter(p=>(p.name+p.description).toLowerCase().includes(q)):currentPlans);
}
qs("#plan-search").addEventListener("input", ()=>{ const q=qs("#plan-search").value.toLowerCase().trim();
  renderPlans(q?currentPlans.filter(p=>(p.name+p.description).toLowerCase().includes(q)):currentPlans); });
qs("#refresh-plans").onclick=loadPlans;

async function loadPurchases(){
  if(!currentUser){ qs("#purchase-list").innerHTML="<div class='muted'>Inicia sesión para ver tus accesos.</div>"; return; }
  const listEl=qs("#purchase-list"); listEl.innerHTML=`<div class="row"><div class="loader"></div><span class="muted">Cargando compras...</span></div>`;
  const r=await api(`/my-purchases?userId=${encodeURIComponent(currentUser.id)}`); if(!r.ok){ listEl.innerHTML="<div class='muted'>Error cargando compras.</div>"; return; }
  const j=r.data; if(!j.purchases?.length){ listEl.innerHTML="<div class='muted'>Aún no tienes compras.</div>"; return; }
  listEl.innerHTML=""; j.purchases.forEach(p=>{
    const el=document.createElement("div"); el.className="item";
    el.innerHTML=`<div><div><strong>Código:</strong> <span class="code">${p.code}</span></div><div class="muted">Plan: ${p.planId} · ${new Date(p.purchasedAt).toLocaleString()}</div></div>
      <div class="row"><button class="btn btn-outline copy" data-code="${p.code}">Copiar</button><button class="btn use" data-code="${p.code}">Usar servicio</button></div>`;
    listEl.appendChild(el);
  });
  qsa("button.copy",listEl).forEach(b=>{ b.onclick=async()=>{ await navigator.clipboard.writeText(b.dataset.code); toast("Código copiado"); }; });
  qsa("button.use",listEl).forEach(b=>{ b.onclick=async()=>{ const code=b.dataset.code;
    const r=await api("/validate",{ method:"POST", body:{ code } }); if(!r.ok){ toast(r.data?.msg||"Código inválido","err"); return; }
    qs("#validate-result").textContent=JSON.stringify(r.data.license,null,2); toast("Acceso concedido por Empresa B (Licencias)."); }; });
}
qs("#form-validate").addEventListener("submit", async (e)=>{ e.preventDefault();
  const code=qs("#code").value.trim(); if(!code) return;
  const r=await api("/validate",{ method:"POST", body:{ code } });
  if(!r.ok){ toast(r.data?.msg||"Código inválido","err"); return; }
  qs("#validate-result").textContent=JSON.stringify(r.data.license,null,2); toast("Código válido."); });

qs("#form-plan").addEventListener("submit", async (e)=>{
  e.preventDefault(); if(!currentUser || currentUser.role!=="admin"){ toast("Solo admin.","err"); return; }
  const name=qs("#p-name").value.trim(), price=Number(qs("#p-price").value), description=qs("#p-desc").value.trim();
  const r=await api("/plans",{ method:"POST", headers:{ "x-admin":"true" }, body:{ name,price,description,createdBy:currentUser.id } });
  if(!r.ok){ toast(r.data?.msg||"No se pudo crear","err"); return; }
  toast("Plan creado."); qs("#p-name").value=""; qs("#p-price").value=""; qs("#p-desc").value=""; show("market"); loadPlans(); loadAdminPlans();
});
async function loadAdminPlans(){
  const el=qs("#admin-plans"); const r=await api("/plans"); if(!r.ok){ el.innerHTML="<div class='muted'>Error cargando planes</div>"; return; }
  const arr=r.data?.plans||[]; if(!arr.length){ el.innerHTML="<div class='muted'>No hay planes.</div>"; return; }
  el.innerHTML=""; arr.forEach(p=>{ const row=document.createElement("div"); row.className="item";
    row.innerHTML=`<div><strong>${p.name}</strong><div class="muted">ID: ${p.id} · $${Number(p.price).toFixed(2)} · ${new Date(p.createdAt||Date.now()).toLocaleString()}</div></div><span class="badge">Empresa A</span>`; el.appendChild(row); });
}

async function loadSOA(){
  const topo=qs("#soa-topology"); topo.innerHTML=`<div class="row"><div class="loader"></div><span class="muted">Cargando topología...</span></div>`;
  const r=await api("/topology"); if(!r.ok){ topo.innerHTML="<div class='muted'>No se pudo obtener topología.</div>"; return; }
  const t=r.data;
  topo.innerHTML=`
    <h3>Componentes y responsabilidades</h3>
    <div class="grid">
      <div class="card"><strong>${t.gateway.name}</strong><div class="muted">${t.gateway.baseUrl}</div></div>
      <div class="card"><strong>${t.orchestrator.name}</strong><div class="muted">${t.orchestrator.baseUrl}</div></div>
      <div class="card"><strong>${t.bus.name}</strong><div class="muted">${t.bus.kind}</div></div>
      ${t.companies.map(c=>`
        <div class="card">
          <div class="row" style="justify-content:space-between;align-items:center">
            <strong>${c.name}</strong><span class="badge">${c.tag}</span>
          </div>
          <ul style="margin-top:8px">${c.services.map(s=>`<li>• ${s.name} <span class="muted">(${s.baseUrl})</span></li>`).join("")}</ul>
        </div>`).join("")}
    </div>
    <p class="muted" style="margin-top:8px"></p>`;
  const h=await api("/health"); qs("#soa-health-pre").textContent=JSON.stringify(h.data,null,2);
}

show("market");
