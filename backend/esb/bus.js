import { resolve } from "./registry.js";

async function callHttp(base, route, payload, headers = {}) {
    const url = (route.method === "GET" && payload && Object.keys(payload).length)
        ? `${base}${route.path}?` + new URLSearchParams(payload).toString()
        : `${base}${route.path}`;

    const res = await fetch(url, {
        method: route.method,
        headers: { "Content-Type":"application/json", ...headers },
        body: route.method === "GET" ? undefined : JSON.stringify(payload || {})
    });
    const text = await res.text();
    let data; try { data = text ? JSON.parse(text) : {}; } catch { data = { ok:false, raw:text }; }
    return { status: res.status, data };
}

export async function send({ service, action, payload = {}, headers = {} }) {
    const svc = resolve(service);
    const route = svc.routes[action];
    if (!route) return { status: 500, data: { ok:false, msg:`Acción ${action} no soportada por ${service}` } };
    try {
        return await callHttp(svc.baseUrl, route, payload, headers);
    } catch (e) {
        return { status: 502, data: { ok:false, msg:`Fallo al invocar ${service}.${action}`, error:String(e) } };
    }
}
