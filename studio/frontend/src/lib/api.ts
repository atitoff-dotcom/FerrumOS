export interface ScriptItem {
  filename: string;
  description: string;
  size: number;
}

export interface NodeTask {
  id: string;
  task_id?: string;
  status: string;
  pins: Record<string, string>;
  execution_count?: number;
  frb_size?: number;
  rhb_size?: number;
  size?: number;
  js_size?: number;
  storage?: 'flash' | 'ram' | string;
  persisted?: boolean;
  live?: boolean;
}

export interface PinInfo {
  pin: number;
  status: 'free' | 'claimed' | 'bus' | 'forbidden';
  owner: string;
}

export interface SharedBusses {
  i2c?: Array<{ alias: string; sda: number; scl: number; devices: string[]; task_id: string }>;
  spi?: Array<{ alias: string; cs: number; mosi: number; task_id: string }>;
  uart?: Array<{ alias: string; tx: number; rx: number; baud: number; task_id: string }>;
}

export interface DigitalTwinState {
  node_id: string;
  online: boolean;
  active_tasks: Record<string, NodeTask>;
  pin_matrix: PinInfo[];
  shared_busses: SharedBusses;
}

export async function fetchScripts(): Promise<ScriptItem[]> {
  const res = await fetch('/api/scripts');
  if (!res.ok) throw new Error('Failed to fetch scripts');
  return res.json();
}

export async function fetchScriptCode(filename: string): Promise<string> {
  const res = await fetch(`/api/scripts/${filename}`);
  if (!res.ok) throw new Error('Failed to read script');
  const data = await res.json();
  return data.code || '';
}

export async function saveScript(filename: string, code: string): Promise<void> {
  const res = await fetch(`/api/scripts/${filename}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code })
  });
  if (!res.ok) throw new Error('Failed to save script');
}

export async function deleteScript(filename: string): Promise<void> {
  const res = await fetch(`/api/scripts/${filename}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete script');
}

export async function fetchDigitalTwin(nodeId = 'c6_supermini_main'): Promise<DigitalTwinState> {
  const res = await fetch(`/api/nodes/${nodeId}/twin`);
  if (!res.ok) throw new Error('Failed to fetch digital twin');
  return res.json();
}

export async function deployScript(nodeId: string, filename: string, code: string): Promise<any> {
  const res = await fetch(`/api/nodes/${nodeId}/deploy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, code, board: 'esp32c6_supermini' })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Deploy failed');
  return data;
}

export async function validateScriptContext(nodeId: string, taskId: string, code: string): Promise<{ valid: boolean; errors: Array<{ message: string }> }> {
  const res = await fetch(`/api/nodes/${nodeId}/validate-context`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, board: 'esp32c6_supermini', task_id: taskId })
  });
  return res.json();
}

export async function commitFlash(nodeId: string): Promise<{ saved_count: number; status?: string; message?: string }> {
  const res = await fetch(`/api/nodes/${nodeId}/flash/commit`, { method: 'POST' });
  let data: any = {};
  try {
    data = await res.json();
  } catch {
    data = {};
  }
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}: Flash commit failed`);
  return data;
}

export async function unloadTask(nodeId: string, taskId: string): Promise<void> {
  const res = await fetch(`/api/nodes/${nodeId}/tasks/${taskId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Unload task failed');
}

export async function testMqtt(nodeId: string): Promise<{ ok: boolean; broker?: string; latency_ms?: number; error?: string; message?: string }> {
  const res = await fetch(`/api/nodes/${nodeId}/mqtt/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host: '192.168.1.114', port: 1883, username: 'alex', password: 'bh0020' })
  });
  return res.json();
}
