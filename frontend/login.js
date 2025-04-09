document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
  
    const response = await fetch("http://localhost:5000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
  
    const data = await response.json();
    if (response.ok) {
      alert("Welcome, " + data.username + " (" + data.role + ")");
      // redirect to role-based page here
    } else {
      document.getElementById("error").textContent = data.message;
    }
  });
  