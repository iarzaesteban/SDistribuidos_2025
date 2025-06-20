import type { TransactionStatus } from "../../../types/types";
import "./EarringTasks.css";

interface InProgressTxsProperties {
    earringTxs: TransactionStatus[];
    showEarring: boolean;
    setShowEarring: (showInProgress: boolean) => void;
}

export const EarringTasks = ({ earringTxs, showEarring, setShowEarring }: InProgressTxsProperties) => (
    <div className='earring-info-container'>
        <p>Cantidad de tareas pendientes: <strong>{earringTxs.length}</strong></p>
        <button className="button ver-mas" onClick={() => setShowEarring(!showEarring)}>
            {showEarring ? "Ocultar tareas" : "Ver tareas"}
        </button>
        {showEarring && earringTxs.length > 0 && (
            <div className="earring-details">
                {earringTxs.map((tx, index) => (
                    <div key={index} className="tx-card">
                        <p><strong>ID Transaccion:</strong> {tx.tx_id}</p>
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