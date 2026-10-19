import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Dropzone from '../components/Dropzone';

describe('Dropzone Component', () => {
  it('renders upload instructions when no file is selected', () => {
    render(
      <Dropzone
        file={null}
        dragActive={false}
        handleDrag={() => {}}
        handleDrop={() => {}}
        handleFileChange={() => {}}
        removeFile={() => {}}
        loadSampleResume={() => {}}
        error=""
      />
    );

    expect(screen.getByText('Upload Resume')).toBeInTheDocument();
    expect(screen.getByText('Drag & drop your resume')).toBeInTheDocument();
    expect(screen.getByText(/PDF, DOCX, TXT formats only/)).toBeInTheDocument();
  });

  it('renders loaded file details and remove button when file is provided', () => {
    const mockFile = new File(['mock content'], 'test_resume.pdf', { type: 'application/pdf' });
    const removeFile = vi.fn();

    render(
      <Dropzone
        file={mockFile}
        dragActive={false}
        handleDrag={() => {}}
        handleDrop={() => {}}
        handleFileChange={() => {}}
        removeFile={removeFile}
        loadSampleResume={() => {}}
        error=""
      />
    );

    expect(screen.getByText('test_resume.pdf')).toBeInTheDocument();
    const removeBtn = screen.getByText('Remove');
    expect(removeBtn).toBeInTheDocument();

    fireEvent.click(removeBtn);
    expect(removeFile).toHaveBeenCalledTimes(1);
  });

  it('displays error banner when error prop is passed', () => {
    render(
      <Dropzone
        file={null}
        dragActive={false}
        handleDrag={() => {}}
        handleDrop={() => {}}
        handleFileChange={() => {}}
        removeFile={() => {}}
        loadSampleResume={() => {}}
        error="File size exceeds 10MB limit."
      />
    );

    expect(screen.getByText('File size exceeds 10MB limit.')).toBeInTheDocument();
  });

  it('triggers sample resume callback when Try Sample is clicked', () => {
    const loadSample = vi.fn();
    render(
      <Dropzone
        file={null}
        dragActive={false}
        handleDrag={() => {}}
        handleDrop={() => {}}
        handleFileChange={() => {}}
        removeFile={() => {}}
        loadSampleResume={loadSample}
        error=""
      />
    );

    const sampleBtn = screen.getByText('Try Sample');
    fireEvent.click(sampleBtn);
    expect(loadSample).toHaveBeenCalledTimes(1);
  });
});
