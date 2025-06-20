import { useState } from 'react';
import './Statistics.css';

import { useBlockchainViewer } from './use-statistics';
import { InProgressTxs } from './InProgressTxs/InProgressTxs';
import { WorkerInfo } from './WorkerInfo/WorkerInfo';
import { EarringTasks } from './EarringTasks/EarringTasks';

export const Statistics = () => {
    const [txId, setTxId] = useState<string>("");
    const [showWorkers, setShowWorkers] = useState<boolean>(false);
    const [showInProgress, setShowInProgress] = useState<boolean>(false);
    const [showEarring, setShowEarring] = useState<boolean>(false);

    const {
        handleSearchTransaction,
        transaction,
        status,
        workers,
        earringTxs,
        inProgressTxs} = useBlockchainViewer();

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (txId) {
            handleSearchTransaction(txId);
        } else {
            alert("No ingresaste ningún id válido")
        }
    };

    return (
        <section className="statistics-container">
            <h1 className="title">Información util</h1>
            {transaction ? (
                <div>
                    <div key={transaction.tx_id} className="data-container">
                        <h2>Transaccion</h2>
                        <p><strong>Status:</strong> {status}</p>
                        <div>
                            <p className="subtitle">Configuracion:</p>
                            <p><strong>Origen:</strong> {transaction.source}</p>
                            <p><strong>Destino:</strong> {transaction.target}</p>
                            <p><strong>Monto:</strong> {transaction.amount}</p>
                            <p><strong>Descripción:</strong> {transaction.description}</p>
                            <p><strong>Timestamp:</strong> {transaction.timestamp}</p>
                            <p><strong>Firma:</strong> {transaction.sign}</p>
                        </div>
                    </div>
                </div>
            ) : <form onSubmit={handleSearch} className='statistics-container__form'>
                <h3>Ver estado de mi tarea</h3>
                <input
                    type="text"
                    value={txId}
                    onChange={(e) => setTxId(e.target.value)}
                    placeholder="Ingrese tx_id"
                />
                <button type="submit" className="button estado">
                    Ver Estado
                </button>
            </form>
            }

            <WorkerInfo
                workers={workers}
                setShowWorkers={setShowWorkers}
                showWorkers={showWorkers}
            />

            <InProgressTxs
                inProgressTxs={inProgressTxs}
                showInProgress={showInProgress}
                setShowInProgress={setShowInProgress}
            />
            <EarringTasks 
                earringTxs={earringTxs} 
                showEarring={showEarring}
                setShowEarring={setShowEarring}
            />

        </section>
    )

};

export default Statistics;