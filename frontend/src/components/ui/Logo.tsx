export function Logo({ size = 64, className = "" }: { size?: number; className?: string }) {
  return (
    <img
      src="/ht-logo.png"
      alt="HT Medical Company"
      className={`object-contain ${className}`}
      style={{ width: size, height: size }}
    />
  );
}
