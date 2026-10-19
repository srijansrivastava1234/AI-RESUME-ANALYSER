import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from '../components/Header';

describe('Header Component', () => {
  it('renders logo title and version badge', () => {
    render(
      <Header
        theme="dark"
        setTheme={() => {}}
        apiOnline={true}
        setShowHelpModal={() => {}}
        appMode="audit"
        setAppMode={() => {}}
      />
    );

    expect(screen.getByText('ATS Resume Analyser AI')).toBeInTheDocument();
    expect(screen.getByText('v1.9.0')).toBeInTheDocument();
    expect(screen.getByText('API: Online')).toBeInTheDocument();
  });

  it('displays Simulation Mode when API is offline', () => {
    render(
      <Header
        theme="dark"
        setTheme={() => {}}
        apiOnline={false}
        setShowHelpModal={() => {}}
        appMode="audit"
        setAppMode={() => {}}
      />
    );

    expect(screen.getByText('API: Simulation Mode')).toBeInTheDocument();
  });

  it('switches app modes when buttons are clicked', () => {
    const setAppMode = vi.fn();
    render(
      <Header
        theme="dark"
        setTheme={() => {}}
        apiOnline={true}
        setShowHelpModal={() => {}}
        appMode="audit"
        setAppMode={setAppMode}
      />
    );

    fireEvent.click(screen.getByText('Batch Compare'));
    expect(setAppMode).toHaveBeenCalledWith('compare');

    fireEvent.click(screen.getByText('XYZ Impact Lab'));
    expect(setAppMode).toHaveBeenCalledWith('xyz');
  });

  it('triggers theme change when theme dots are clicked', () => {
    const setTheme = vi.fn();
    render(
      <Header
        theme="dark"
        setTheme={setTheme}
        apiOnline={true}
        setShowHelpModal={() => {}}
        appMode="audit"
        setAppMode={() => {}}
      />
    );

    const emeraldBtn = screen.getByTitle('Emerald Green');
    fireEvent.click(emeraldBtn);
    expect(setTheme).toHaveBeenCalledWith('emerald');
  });
});
