export const REGISTRY = {
    AUTH: {
        name: "Auth Service",
        baseUrl: "http://localhost:3001",
        routes: {
            REGISTER: { method: "POST", path: "/register" },
            LOGIN:    { method: "POST", path: "/login"  },
            HEALTH:   { method: "GET",  path: "/health" }
        }
    },
    CATALOG: {
        name: "Catalog Service (Empresa A)",
        baseUrl: "http://localhost:3002",
        routes: {
            LIST_PLANS:  { method: "GET",  path: "/plans"  },
            CREATE_PLAN: { method: "POST", path: "/plans"  },
            HEALTH:      { method: "GET",  path: "/health" }
        }
    },
    ORDER: {
        name: "Order/Licensing Service (Empresa B)",
        baseUrl: "http://localhost:3003",
        routes: {
            PURCHASE:       { method: "POST", path: "/purchase"   },
            LIST_PURCHASES: { method: "GET",  path: "/purchases"  },
            VALIDATE:       { method: "POST", path: "/validate"   },
            HEALTH:         { method: "GET",  path: "/health"     }
        }
    }
};

export function resolve(serviceKey) {
    const s = REGISTRY[serviceKey];
    if (!s) throw new Error(`Servicio no registrado: ${serviceKey}`);
    return s;
}
