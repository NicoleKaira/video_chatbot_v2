import {EventSourceParserStream} from "eventsource-parser/stream";

export async function* parseSSEStream(stream: any): AsyncGenerator<string> {
  if (stream !== null) {
    const sseStream = stream
      .pipeThrough(new TextDecoderStream())
      .pipeThrough(new EventSourceParserStream());

    for await (const chunk of sseStream) {
      if (chunk.type === 'event') {
        yield chunk.data;
      }
    }
  }
}
