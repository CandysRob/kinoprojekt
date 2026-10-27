// Väike fetch-ümbris Django API jaoks (/api/...).

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildUrl(path, params = {}) {
  const url = new URL(`/api/${path}`, window.location.origin);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  }
  return url;
}

export async function apiGet(path, params, { signal } = {}) {
  let response;
  try {
    response = await fetch(buildUrl(path, params), { headers: { Accept: "application/json" }, signal });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError("Serveriga ei saanud ühendust.", 0);
  }
  if (!response.ok) {
    const message = response.status === 404 ? "Ei leitud." : `Päring ebaõnnestus (${response.status}).`;
    throw new ApiError(message, response.status);
  }
  return response.json();
}
