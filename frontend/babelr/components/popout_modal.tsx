import { useRef, useEffect, ReactNode } from "react";
import styles from "../stylesheets/modal.module.css"

interface ModalProps {
  isOpen: boolean;
  hasCloseBtn?: boolean;
  onClose?: () => void;
  children: ReactNode;
}

const Modal = ({ isOpen, hasCloseBtn = false, onClose, children }: ModalProps) => {
  const modalRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const modalElement = modalRef.current;
    if (!modalElement) return;

    if (isOpen) {
      modalElement.showModal();
    } else {
      modalElement.close();
    }
  }, [isOpen]);

  const handleCloseModal = () => {
    if (onClose) onClose();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDialogElement>) => {
    if (event.key === "Escape") {
      handleCloseModal();
    }
  };

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className={styles["modal"]}>
      <div className={styles["modal-content"]}>
        {hasCloseBtn && (
          <button className={styles["modal-close-btn"]} onClick={handleCloseModal} aria-label="Close Modal">
            ✖
          </button>
        )}
        {children}
      </div>
    </dialog>
  );
};

export default Modal;