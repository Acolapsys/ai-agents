const API_BASE = 'http://localhost:8000';

export async function chatWithAgent(agentName, message, userId = 'web_user', chatId = 'web') {
  const response = await fetch(`${API_BASE}/chat/${agentName}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      user_id: userId,
      chat_id: chatId,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error (${response.status}): ${error}`);
  }

  return response.json();
}