import { CheckCircle2, X, XCircle } from "lucide-react";

interface ToastProps {
  type: "success" | "error";
  message: string;
  onClose: () => void;
}

export default function Toast({ type, message, onClose }: ToastProps) {
  const isSuccess = type === "success";

  return (
    <div
      className={`toast toast-${type}`}
      role={isSuccess ? "status" : "alert"}
      aria-live="polite"
    >
      {isSuccess ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
      <span>{message}</span>
      <button
        type="button"
        className="toast-close"
        onClick={onClose}
        aria-label="Đóng thông báo"
      >
        <X size={16} />
      </button>
    </div>
  );
}
