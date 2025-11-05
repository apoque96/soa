import express from "express";
import cors from "cors";
import { v4 as uuid } from "uuid";

const app = express();
app.use(cors());
app.use(express.json());

const users = [
  { id: "u-admin", name: "Admin", email: "admin@soa.dev", password: "admin123", role: "admin" }
];

app.post("/register", (req, res) => {
  const { name, email, password } = req.body || {};
  if (!name || !email || !password) return res.status(400).json({ ok:false, msg:"name, email, password requeridos" });
  if (users.some(u=>u.email===email)) return res.status(409).json({ ok:false, msg:"Email ya registrado" });
  const user = { id:uuid(), name, email, password, role:"customer" };
  users.push(user);
  res.json({ ok:true, user:{ id:user.id, name, email, role:user.role }});
});

app.post("/login", (req, res) => {
  const { email, password } = req.body || {};
  const user = users.find(u=>u.email===email && u.password===password);
  if(!user) return res.status(401).json({ ok:false, msg:"Credenciales inválidas" });
  res.json({ ok:true, user:{ id:user.id, name:user.name, email:user.email, role:user.role }});
});

app.get("/health", (_req,res)=> res.json({ ok:true, service:"auth", port:3001, users:users.length }));

const PORT = 3001;
app.listen(PORT, ()=> console.log(`Auth Service en http://localhost:${PORT}`));
