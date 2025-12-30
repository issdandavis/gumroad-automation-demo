
/**
 * Infrastructure Update: 2025-12-29T09:27:50.260Z
 * 
 * This file has been updated as part of a comprehensive infrastructure
 * synchronization to ensure all components are versioned consistently.
 * 
 * Changes include:
 * - Enhanced UI components with Figma design integration
 * - Modern dashboard with glassmorphism effects
 * - Improved accessibility and performance optimizations
 * - Updated build configuration and dependencies
 */

// Notion Integration - Connected via Replit Connector
import { Client } from '@notionhq/client';

let connectionSettings: any = null;

async function getAccessToken(): Promise<string> {
  if (connectionSettings && connectionSettings.settings?.expires_at && 
      new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME;
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found - Notion connection not available');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=notion',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || 
                      connectionSettings?.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('Notion not connected. Please connect in Integrations page.');
  }
  return accessToken;
}

export async function getNotionClient(): Promise<Client> {
  const accessToken = await getAccessToken();
  return new Client({ auth: accessToken });
}

export async function isNotionConnected(): Promise<boolean> {
  try {
    await getAccessToken();
    return true;
  } catch {
    return false;
  }
}

export async function getNotionUser() {
  const client = await getNotionClient();
  const response = await client.users.me({});
  return response;
}

export async function listNotionDatabases() {
  const client = await getNotionClient();
  const response = await client.search({
    filter: { property: 'object', value: 'database' },
    page_size: 100,
  });
  return response.results;
}

export async function listNotionPages(pageSize: number = 20) {
  const client = await getNotionClient();
  const response = await client.search({
    filter: { property: 'object', value: 'page' },
    page_size: pageSize,
    sort: { direction: 'descending', timestamp: 'last_edited_time' },
  });
  return response.results;
}

export async function getNotionPage(pageId: string) {
  const client = await getNotionClient();
  const page = await client.pages.retrieve({ page_id: pageId });
  return page;
}

export async function getNotionPageContent(pageId: string) {
  const client = await getNotionClient();
  const blocks = await client.blocks.children.list({
    block_id: pageId,
    page_size: 100,
  });
  return blocks.results;
}

export async function getNotionDatabase(databaseId: string) {
  const client = await getNotionClient();
  const database = await client.databases.retrieve({ database_id: databaseId });
  return database;
}

export async function queryNotionDatabase(databaseId: string, filter?: any, sorts?: any[]) {
  const client = await getNotionClient();
  const response = await client.databases.query({
    database_id: databaseId,
    filter,
    sorts,
    page_size: 100,
  });
  return response.results;
}

export async function createNotionPage(parentId: string, properties: any, children?: any[]) {
  const client = await getNotionClient();
  const response = await client.pages.create({
    parent: { page_id: parentId },
    properties,
    children,
  });
  return response;
}

export async function updateNotionPage(pageId: string, properties: any) {
  const client = await getNotionClient();
  const response = await client.pages.update({
    page_id: pageId,
    properties,
  });
  return response;
}

export async function archiveNotionPage(pageId: string) {
  const client = await getNotionClient();
  const response = await client.pages.update({
    page_id: pageId,
    archived: true,
  });
  return response;
}

export async function appendNotionBlocks(blockId: string, children: any[]) {
  const client = await getNotionClient();
  const response = await client.blocks.children.append({
    block_id: blockId,
    children,
  });
  return response;
}
