
import express from "express";
import session from "express-session";
import bodyParser from "body-parser";
const app = express();
app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({ secret: "dev-secret", resave: false, saveUninitialized: true }));

const users = [
  { id: 1, username: "alice", password: "password123", secretNote: "Alice ka secret" },
  { id: 2, username: "bob",   password: "qwerty",     secretNote: "Bob ka secret" }
];

app.get("/", (req, res) => {
  res.render("index", { user: req.session.user });
});

app.get("/login", (req, res) => {
  res.render("login", { error: null });
});

app.post("/login", (req, res) => {
 
  const { username, password } = req.body;
  const user = users.find(u => u.username === username && u.password === password);
  if (user) {
    req.session.user = { id: user.id, username: user.username };
    return res.redirect("/");
  }
  res.render("login", { error: "Invalid creds" });
});

// Insecure direct object reference example
app.get("/note/:userid", (req, res) => {
  // No authorization check — intentionally vulnerable
  const uid = Number(req.params.userid);
  const user = users.find(u => u.id === uid);
  if (!user) return res.status(404).send("Not found");
  res.send(`<h3>Secret note for user ${uid}:</h3><pre>${user.secretNote}</pre>`);
});

app.get("/search", (req, res) => {
  const q = req.query.q || "";
  // Note: intentionally reflecting user input without encoding — vulnerable to XSS in this demo
  res.send(`<h1>Search results for: ${q}</h1><p>Results...</p>`);
});

app.get("/logout", (req, res) => {
  req.session.destroy(()=>{ res.redirect("/"); });
});

app.listen(3000, ()=>console.log("Vuln CTF app running at http://localhost:3000"));
