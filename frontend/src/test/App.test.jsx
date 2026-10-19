import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

describe('App Smoke Test', () => {
  beforeEach(() => {
    // Mock fetch for healthcheck and API calls
    global.fetch = vi.fn().mockImplementation((url) => {
      if (url.includes('/api/health') || url.includes('/health')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'ok', version: '3.8.0' }),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    });
  });

  it('renders application header, sidebar upload, and initial welcome screen', async () => {
    render(<App />);

    // Header logo text
    expect(screen.getByText('ATS Resume Analyser AI')).toBeInTheDocument();

    // Welcome placeholder
    expect(screen.getByText('Ready to Audit Your Resume?')).toBeInTheDocument();
    expect(
      screen.getByText(/Upload your resume in PDF, DOCX, or TXT format/)
    ).toBeInTheDocument();

    // Healthcheck turns API status online
    await waitFor(() => {
      expect(screen.getByText('API: Online')).toBeInTheDocument();
    });
  });
});
