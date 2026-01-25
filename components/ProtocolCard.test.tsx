import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProtocolCard from './ProtocolCard';
import { ProtocolDetail } from '../types';
import { explainConcept } from '../services/geminiService';
import { vi, expect, test } from 'vitest';
import '@testing-library/jest-dom';

// Mock the service
vi.mock('../services/geminiService', () => ({
  explainConcept: vi.fn(() => Promise.resolve('Mocked Explanation')),
}));

const mockProtocol: ProtocolDetail = {
  title: 'Test Protocol',
  description: 'Test Description',
  mechanism: 'Test Mechanism',
  frameworkIntegration: 'Test Integration'
};

test('ProtocolCard makes API call only once when explanation is toggled (Optimized)', async () => {
  render(<ProtocolCard protocol={mockProtocol} />);

  const button = screen.getByRole('button', { name: /Explain with AI/i });

  // First Click: Open
  fireEvent.click(button);

  // Wait for explanation
  await waitFor(() => {
    expect(screen.getByText('Mocked Explanation')).toBeInTheDocument();
  });

  expect(explainConcept).toHaveBeenCalledTimes(1);

  // Second Click: Hide
  fireEvent.click(button);
  expect(screen.queryByText('Mocked Explanation')).not.toBeInTheDocument();

  // Third Click: Open Again
  fireEvent.click(button);

  // Explanation should appear immediately (or after re-render)
  await waitFor(() => {
     expect(screen.getByText('Mocked Explanation')).toBeInTheDocument();
  });

  // Verify it was NOT called again (Still 1)
  expect(explainConcept).toHaveBeenCalledTimes(1);
});
