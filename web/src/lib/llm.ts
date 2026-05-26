import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";

let anthropicClient: Anthropic | null = null;
let openaiClient: OpenAI | null = null;

function getAnthropic(): Anthropic | null {
  if (!process.env.ANTHROPIC_API_KEY) return null;
  if (!anthropicClient) {
    anthropicClient = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  }
  return anthropicClient;
}

function getOpenAI(): OpenAI | null {
  if (!process.env.OPENAI_API_KEY) return null;
  if (!openaiClient) {
    openaiClient = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  }
  return openaiClient;
}

async function callClaude(
  system: string,
  userMessage: string,
  maxTokens = 4096,
  temperature = 0.3
): Promise<string> {
  const client = getAnthropic();
  if (!client) throw new Error("Anthropic API key not configured");

  const resp = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: maxTokens,
    temperature,
    system,
    messages: [{ role: "user", content: userMessage }],
  });

  const block = resp.content[0];
  if (block.type === "text") return block.text;
  throw new Error("Unexpected response type from Claude");
}

async function callOpenAI(
  system: string,
  userMessage: string,
  maxTokens = 4096,
  temperature = 0.3
): Promise<string> {
  const client = getOpenAI();
  if (!client) throw new Error("OpenAI API key not configured");

  const resp = await client.chat.completions.create({
    model: "gpt-4o",
    max_tokens: maxTokens,
    temperature,
    messages: [
      { role: "system", content: system },
      { role: "user", content: userMessage },
    ],
  });

  return resp.choices[0]?.message?.content || "";
}

export async function generate(
  system: string,
  userMessage: string,
  maxTokens = 4096,
  temperature = 0.3,
  prefer: "claude" | "openai" = "claude"
): Promise<string> {
  const providers =
    prefer === "claude"
      ? [callClaude, callOpenAI]
      : [callOpenAI, callClaude];

  let lastError: Error | null = null;
  for (const fn of providers) {
    try {
      return await fn(system, userMessage, maxTokens, temperature);
    } catch (e) {
      lastError = e instanceof Error ? e : new Error(String(e));
    }
  }
  throw new Error(`All LLM providers failed: ${lastError?.message}`);
}

export async function generateJSON<T = unknown>(
  system: string,
  userMessage: string,
  maxTokens = 4096,
  temperature = 0.2
): Promise<T> {
  const fullSystem =
    system +
    "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown fences, no commentary.";
  const raw = await generate(fullSystem, userMessage, maxTokens, temperature);
  let cleaned = raw.trim();
  if (cleaned.startsWith("```")) {
    const lines = cleaned.split("\n").filter((l) => !l.trim().startsWith("```"));
    cleaned = lines.join("\n");
  }
  return JSON.parse(cleaned) as T;
}
