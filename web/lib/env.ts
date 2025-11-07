const requiredServerVariables = ["OPENAI_API_KEY"] as const;

type RequiredServerVariable = (typeof requiredServerVariables)[number];

function ensureServerEnv(): Record<RequiredServerVariable, string> {
  if (typeof window !== "undefined") {
    throw new Error("ensureServerEnv should only be used on the server");
  }

  const values = {} as Record<RequiredServerVariable, string>;

  for (const key of requiredServerVariables) {
    const value = process.env[key];
    if (!value) {
      throw new Error(`Missing required server environment variable: ${key}`);
    }
    values[key] = value;
  }

  return values;
}

export const clientEnv = {
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME ?? "Unified AI Lab"
} as const;

export const serverEnv = () => ensureServerEnv();
