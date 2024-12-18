import { Chat } from "@/components/Chat/Chat";
import { Footer } from "@/components/Layout/Footer";
import { Navbar } from "@/components/Layout/Navbar";
import { Message } from "@/types";
import Head from "next/head";
import { useEffect, useRef, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [initializing, setInitializing] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const chatbotContent = `Hallo! Hast du Fragen zum Grundgesetz?`;

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async (message: Message) => {
    const updatedMessages = [...messages, message];
    setMessages(updatedMessages);
    setLoading(true);

    const request: RequestInit = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: { role: "user", content: message.content} as Message} ),
    };

    const response = await fetch("/api/chat", request);
    if (!response.ok) {
      setLoading(false);
      throw new Error(response.statusText);
    }
    const responseData = await response.json();
    const messageContent = responseData.message?.content;

    if (!messageContent) {
      return;
    }

    setLoading(false);
    let done = false;
    let isFirst = true;

    while (!done) {
      done = true;
      if (isFirst) {
        isFirst = false;
        setMessages((messages) => [
          ...messages,
          {
            role: "assistant",
            content: messageContent
          }
        ]);
      } else {
        setMessages((messages) => {
          const lastMessage = messages[messages.length - 1];
          const updatedMessage = {
            ...lastMessage,
            content: lastMessage.content + messageContent
          };
          return [...messages.slice(0, -1), updatedMessage];
        });
      }
    }
  };

  const handleReset = (chatbotContent: string) => {
    setMessages([
      {
        role: "assistant",
        content: chatbotContent
      }
    ]);
  };

  useEffect(() => {
    const initializeChatbot = async () => {
      try {
        const response = await fetch("/api/initialization");
        if (!response.ok) {
          throw new Error(response.statusText);
        }
        setMessages([
          {
            role: "assistant",
            content: chatbotContent,
          },
        ]);
        setInitializing(false);
      } catch (error : any) {
        setErrorMessage(error.toString());
      }
    };
    initializeChatbot();
  }, [chatbotContent]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <>
      <Head>
        <title>RechtChecker</title>
        <meta
          name="description"
          content="A simple chatbot starter kit for OpenAI's chat model using Next.js, TypeScript, and Tailwind CSS."
        />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1"
        />
        <link
          rel="icon"
          href="/favicon.ico"
        />
      </Head>

      <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex-1 flex items-center justify-center overflow-auto sm:px-10 pb-4 sm:pb-10">
        <div className="max-w-[800px] w-full mx-auto">
          {initializing ? (
            errorMessage !== '' ? (
              <>
                <div className="text-center text-lg font-bold">Initialization Error:</div>
                <div className="text-center text-lg">&quot;{errorMessage}&quot;</div>
              </>
            ) : (
              <div className="text-center text-lg font-bold">Initializing...</div>
            )
          ) : (
            <>
              <Chat
                messages={messages}
                loading={loading}
                onSend={handleSend}
                onReset={() => handleReset(chatbotContent)}
              />
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>
      <Footer />
      </div>
    </>
  );
}
