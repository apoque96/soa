export function requireFields(obj, fields = []) {
    for (const f of fields) if (obj[f] === undefined || obj[f] === null || obj[f] === "") {
        return { ok:false, msg:`Campo requerido: ${f}` };
    }
    return { ok:true };
}

export const Contracts = {
    REGISTER: { required: ["name","email","password"] },
    LOGIN:    { required: ["email","password"] },
    CREATE_PLAN: { required: ["name","price"] },
    PURCHASE: { required: ["userId","planId"] },
    VALIDATE: { required: ["code"] },
    LIST_PURCHASES: { required: ["userId"] }
};

export function validateContract(type, payload) {
    const c = Contracts[type];
    if (!c) return { ok:true }; // sin contrato
    return requireFields(payload, c.required);
}
