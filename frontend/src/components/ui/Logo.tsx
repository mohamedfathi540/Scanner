import { BookOpenText } from "lucide-react";

export function Logo({ size = 64, className = "" }: { size?: number; className?: string }) {
  return (
    <div 
      className={`flex items-center justify-center bg-primary-600 text-white rounded-xl shadow-sm ${className}`} 
      style={{ width: size, height: size }}
    >
      <BookOpenText size={size * 0.6} strokeWidth={1.5} />
    </div>
  );
}
