import type { AppContext } from "../types";
import { success, error } from "../utils/responses";

const SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech/stream";

export interface TTSRequest {
  text: string;
  target_language_code?: string;
  speaker?: string;
  model?: string;
  pace?: number;
  speech_sample_rate?: number;
  output_audio_codec?: "mp3" | "wav" | "ogg";
  enable_preprocessing?: boolean;
}

async function streamTTS(
  apiKey: string,
  text: string,
  options: {
    target_language_code?: string;
    speaker?: string;
    model?: string;
    pace?: number;
    speech_sample_rate?: number;
    output_audio_codec?: string;
    enable_preprocessing?: boolean;
  } = {}
): Promise<Response> {
  const {
    target_language_code = "hi-IN",
    speaker = "shubh",
    model = "bulbul:v3",
    pace = 1.0,
    speech_sample_rate = 22050,
    output_audio_codec = "mp3",
    enable_preprocessing = true,
  } = options;

  return fetch(SARVAM_TTS_URL, {
    method: "POST",
    headers: {
      "api-subscription-key": apiKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      target_language_code,
      speaker,
      model,
      pace,
      speech_sample_rate,
      output_audio_codec,
      enable_preprocessing,
    }),
  });
}

export async function textToSpeech(c: AppContext) {
  const body = await c.req.json();
  const {
    text,
    target_language_code = "hi-IN",
    speaker = "shubh",
    model = "bulbul:v3",
    pace = 1.0,
    speech_sample_rate = 22050,
    output_audio_codec = "mp3",
    enable_preprocessing = true,
  } = body as TTSRequest;

  if (!text || typeof text !== "string") {
    return error(c, "text is required", 400);
  }

  const apiKey = c.env.SARVAM_API_KEY;
  if (!apiKey) {
    return error(c, "SARVAM_API_KEY not configured", 500);
  }

  try {
    const response = await streamTTS(apiKey, text, {
      target_language_code,
      speaker,
      model,
      pace,
      speech_sample_rate,
      output_audio_codec,
      enable_preprocessing,
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error("Sarvam TTS error:", errText);
      return error(c, `TTS API error: ${response.status}`, 500);
    }

    const contentType = output_audio_codec === "mp3"
      ? "audio/mpeg"
      : output_audio_codec === "wav"
        ? "audio/wav"
        : "audio/ogg";

    return new Response(response.body, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "no-cache",
      },
    });
  } catch (err) {
    console.error("TTS error:", err);
    return error(c, err instanceof Error ? err.message : "TTS failed", 500);
  }
}

export async function chatWithVoice(c: AppContext) {
  const body = await c.req.json();
  const { message, thread_id, tts_options } = body;

  if (!message || typeof message !== "string") {
    return error(c, "message is required", 400);
  }

  const apiKey = c.env.SARVAM_API_KEY;
  if (!apiKey) {
    return error(c, "SARVAM_API_KEY not configured", 500);
  }

  try {
    const { configure, graph, getConfig } = await import("podd-loci");
    const { HumanMessage } = await import("@langchain/core/messages");

    const config = getConfig();
    if (!config.locusGraphAgentSecret) {
      configure({
        locusGraphServerUrl: c.env.LOCUSGRAPH_SERVER_URL,
        locusGraphAgentSecret: c.env.LOCUSGRAPH_AGENT_SECRET || c.env.LOCUSGRAPH_JWT_PRIVATE_KEY,
        locusGraphGraphId: c.env.LOCUSGRAPH_GRAPH_ID,
        openaiApiKey: c.env.OPENAI_API_KEY,
        openaiModel: c.env.OPENAI_MODEL,
      });
    }

    const user = c.get("user");
    const threadId = thread_id || `thread_${user.id}_${Date.now()}`;
    const threadConfig = { configurable: { thread_id: threadId } };

    const result = await graph.invoke(
      {
        messages: [new HumanMessage(message)],
        user_id: user.id,
        user_name: user.name,
      },
      threadConfig,
    );

    const lastMessage = result.messages.at(-1);
    const responseText = typeof lastMessage?.content === "string"
      ? lastMessage.content
      : JSON.stringify(lastMessage?.content);

    const ttsResponse = await streamTTS(apiKey, responseText, tts_options);

    if (!ttsResponse.ok) {
      const errText = await ttsResponse.text();
      console.error("Sarvam TTS error:", errText);
      return error(c, `TTS API error: ${ttsResponse.status}`, 500);
    }

    const output_audio_codec = tts_options?.output_audio_codec || "mp3";
    const contentType = output_audio_codec === "mp3"
      ? "audio/mpeg"
      : output_audio_codec === "wav"
        ? "audio/wav"
        : "audio/ogg";

    return new Response(ttsResponse.body, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "no-cache",
        "X-Thread-Id": threadId,
        "X-Session-Title": result.session_title || "",
        "X-Response-Text": encodeURIComponent(responseText || ""),
      },
    });
  } catch (err) {
    console.error("Chat with voice error:", err);
    return error(c, err instanceof Error ? err.message : "Chat with voice failed", 500);
  }
}

export async function streamChatWithVoice(c: AppContext) {
  const body = await c.req.json();
  const { message, thread_id, tts_options } = body;

  if (!message || typeof message !== "string") {
    return error(c, "message is required", 400);
  }

  const apiKey = c.env.SARVAM_API_KEY;
  if (!apiKey) {
    return error(c, "SARVAM_API_KEY not configured", 500);
  }

  const output_audio_codec = tts_options?.output_audio_codec || "mp3";
  const contentType = output_audio_codec === "mp3"
    ? "audio/mpeg"
    : output_audio_codec === "wav"
      ? "audio/wav"
      : "audio/ogg";

  const encoder = new TextEncoder();

  const readable = new ReadableStream({
    async start(controller) {
      try {
        const { configure, graph, getConfig } = await import("podd-loci");
        const { HumanMessage } = await import("@langchain/core/messages");

        const config = getConfig();
        if (!config.locusGraphAgentSecret) {
          configure({
            locusGraphServerUrl: c.env.LOCUSGRAPH_SERVER_URL,
            locusGraphAgentSecret: c.env.LOCUSGRAPH_AGENT_SECRET || c.env.LOCUSGRAPH_JWT_PRIVATE_KEY,
            locusGraphGraphId: c.env.LOCUSGRAPH_GRAPH_ID,
            openaiApiKey: c.env.OPENAI_API_KEY,
            openaiModel: c.env.OPENAI_MODEL,
          });
        }

        const user = c.get("user");
        const threadId = thread_id || `thread_${user.id}_${Date.now()}`;
        const threadConfig = { configurable: { thread_id: threadId } };

        let fullText = "";
        let sentenceBuffer = "";

        const stream = await graph.stream(
          {
            messages: [new HumanMessage(message)],
            user_id: user.id,
            user_name: user.name,
          },
          { ...threadConfig, streamMode: "values" },
        );

        const sentenceEnders = /[.!?।]\s*/;

        for await (const event of stream) {
          const evt = event as unknown as Record<string, unknown>;
          const messages = (evt.messages || []) as Array<{ content?: string | Array<unknown> }>;
          const lastMsg = messages.at(-1);

          if (lastMsg?.content) {
            const chunk = typeof lastMsg.content === "string"
              ? lastMsg.content.slice(fullText.length)
              : "";

            if (chunk) {
              fullText += chunk;
              sentenceBuffer += chunk;

              const parts = sentenceBuffer.split(sentenceEnders);
              
              while (parts.length > 1) {
                const sentence = parts.shift()!.trim();
                if (sentence) {
                  const sentenceWithPunctuation = sentence + ".";
                  console.log("Streaming TTS for:", sentenceWithPunctuation);

                  const ttsResponse = await streamTTS(apiKey, sentenceWithPunctuation, tts_options);

                  if (ttsResponse.ok && ttsResponse.body) {
                    const reader = ttsResponse.body.getReader();
                    while (true) {
                      const { done, value } = await reader.read();
                      if (done) break;
                      controller.enqueue(value);
                    }
                  }
                }
              }

              sentenceBuffer = parts[0] || "";
            }
          }
        }

        if (sentenceBuffer.trim()) {
          const sentence = sentenceBuffer.trim();
          console.log("Streaming TTS for (final):", sentence);

          const ttsResponse = await streamTTS(apiKey, sentence, tts_options);

          if (ttsResponse.ok && ttsResponse.body) {
            const reader = ttsResponse.body.getReader();
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              controller.enqueue(value);
            }
          }
        }

        controller.close();
      } catch (err) {
        console.error("Stream chat with voice error:", err);
        const errorMessage = err instanceof Error ? err.message : "Stream failed";
        controller.enqueue(encoder.encode(`\n[ERROR: ${errorMessage}]`));
        controller.close();
      }
    },
  });

  return new Response(readable, {
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
