import type { TransactionStatus } from "../../../types/types";
import "./InProgressTxs.css";

interface InProgressTxsProperties {
    inProgressTxs: TransactionStatus[];
    showInProgress: boolean;
    setShowInProgress: (showInProgress: boolean) => void;
}

export const InProgressTxs = ({ inProgressTxs, showInProgress, setShowInProgress }: InProgressTxsProperties) => (
    <div className='in-progress-info-container'>
        <p>Cantidad de tareas en proceso: <strong>{inProgressTxs?.length ?? 0}</strong></p>
        <button className="button ver-mas" onClick={() => setShowInProgress(!showInProgress)}>
            {showInProgress ? "Ocultar tareas" : "Ver tareas"}
        </button>

        {showInProgress && inProgressTxs !== undefined && (
            <div className="in-progress-details">
                {inProgressTxs.map((tx: TransactionStatus, index: number) => (
                    <div key={index} className="tx-card">
                        <p><strong>ID Transacción:</strong> {tx.tx_id}</p>
                        <p><strong>Origen:</strong> {tx.source}</p>
                        <p><strong>Destino:</strong> {tx.target}</p>
                        <p><strong>Monto:</strong> {tx.amount}</p>
                        <p><strong>Estado:</strong> {tx.status}</p>
                        <p><strong>Intentos:</strong> {tx.tries}</p>
                    </div>
                ))}
            </div>
        )}
    </div>
)