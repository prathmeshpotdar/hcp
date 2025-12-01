const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function post(path, body) {
  const url = `${API_BASE}${path}`;
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
}

export default { post };
