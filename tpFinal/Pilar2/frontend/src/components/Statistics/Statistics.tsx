import { useState } from 'react';
import './Statistics.css';

import { useBlockchainViewer } from './use-statistics';

export const Statistics = () => {
    const [txId, setTxId] = useState<string>("");
    const [showWorkers, setShowWorkers] = useState<boolean>(false);

    const { handleSearchTransaction, transaction, status, workers, error } = useBlockchainViewer();

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (txId) {
            handleSearchTransaction(txId);
        }else{
            alert("No ingresaste ningún id válido")
        }
    };

    return (
        <section className="statistics-container">
            <h1 className="title">Información util</h1>
            {transaction ? (
                <div>
                    <p><strong>Status:</strong> {status}</p>
                    <pre>{JSON.stringify(transaction, null, 2)}</pre>
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

            <div className='worker-info-container'>
                <p>Cantidad de workers registrados: <strong>{workers.length}</strong></p>
                <button className="button ver-mas" onClick={() => setShowWorkers(!showWorkers)}>
                    {showWorkers ? "Ocultar detalles" : "Ver más"}
                </button>

                {showWorkers && (
                    <div className="workers-details">
                        {workers.map((worker, index) => (
                            <div key={index} className="worker-card">
                                <p><strong>IP:</strong> {worker.ip}</p>
                                <p><strong>Tipo:</strong> {worker.info.type}</p>
                                <p><strong>Puerto:</strong> {worker.info.port}</p>
                                <p><strong>PubKey:</strong> {worker.info.pub_key}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            {error && <p className="text-red-500 mt-4">{error}</p>}

        </section>
    )

};

export default Statistics;