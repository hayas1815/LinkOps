import { Upload } from 'lucide-react';

import { Button } from '@/components/ui/button';

export function UploadCard() {
  return (
    <div className="rounded-card border border-dashed border-border bg-panel p-8 shadow-sm">
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="rounded-full bg-card p-4 text-brand-primary">
          <Upload className="h-6 w-6" aria-hidden="true" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-text-primary">Drag and drop files here</h3>
          <p className="mt-2 text-sm leading-6 text-text-secondary">Upload documents for processing, classification, and future knowledge extraction.</p>
        </div>
        <Button variant="secondary">Browse files</Button>
      </div>
    </div>
  );
}
