import axios from "axios";
import { COORDINADOR_URL } from "../../constants";
import { useEffect, useState } from "react";
import type { TransactionResponse, TransactionStatus, RegisteredWorkersResponse, InProgressTxResponse, EarringQueueResponse, GenesisBlockType } from "../../types/types";

export const useStatistics = () => {
    const [genesisBlock, setGenesisBlock] = useState<GenesisBlockType | null>(null);
    const [currentWindow, setCurrentWindow] = useState<string>("Calculando ventana...");
    const [error, setError] = useState<string>("");
    const [transaction, setTransaction] = useState<TransactionStatus | null>(null);
    const [status, setStatus] = useState<string>("");
    const [workers, setWorkers] = useState<RegisteredWorkersResponse["workers"]>([]);
    const [inProgressTxs, setInProgressTxs] = useState<TransactionStatus[]>([]);
    const [earringTxs, setEarringTxs] = useState<TransactionStatus[]>([]);

    useEffect(() => {
        const fetchWorkers = async () => {
            try {
                const response = await axios.get<RegisteredWorkersResponse>(
                    `${COORDINADOR_URL}/registered-workers`
                );
                setWorkers(response.data.workers);
                setError("");
            } catch (err) {
                setError("Error al obtener los workers");
                console.error(err);
            }
        };

        fetchWorkers();
    }, []);

    useEffect(() => {
        const fetchInProgressTxs = async () => {
            try {
                const response = await axios.get<InProgressTxResponse>(
                    `${COORDINADOR_URL}/get-in-progress-txs`
                );
                setInProgressTxs(response.data.transactions);
                setError("");
            } catch (err) {
                setError("Error al obtener tareas en progreso");
                console.error(err);
            }
        };

        fetchInProgressTxs();

        const interval = setInterval(fetchInProgressTxs, 10000);

        return () => clearInterval(interval);
    }, []);


    const fetchGenesisBlock = async () => {
        try {
            const response = await axios.get(`${COORDINADOR_URL}/genesis-block`);
            setGenesisBlock(response.data);
            setError("");
        } catch (err) {
            setError("Error al obtener el bloque GENESIS");
            console.error(err);
        }
    };

    const calculateCurrentWindow = (genesisBlock: GenesisBlockType) => {
        const cycleTime = genesisBlock.config.window_period_seconds;
        const now = new Date();
        const seconds = now.getSeconds();
        const positionInCycle = seconds % cycleTime;

        const {
            monitoring_window_start,
            monitoring_window_end,
            publish_window_start,
            publish_window_end,
            window_period_seconds
        } = genesisBlock.config;

        if (positionInCycle >= monitoring_window_start && positionInCycle <= monitoring_window_end) {
            return "Ventana actual: Solicitar tareas";
        } else if (positionInCycle > monitoring_window_end && positionInCycle < publish_window_start) {
            return "Ventana actual: Minado";
        } else if (positionInCycle >= publish_window_start && positionInCycle <= publish_window_end) {
            return "Ventana actual: Publicación de tareas";
        } else if (positionInCycle > publish_window_end && positionInCycle <= window_period_seconds) {
            return "Ventana actual: Validando y encadenando";
        } else {
            return "Ventana actual: Moviendo tareas";
        }
    };

    useEffect(() => {
        fetchGenesisBlock();
    }, []);

    useEffect(() => {
        if (!genesisBlock) return;

        const interval = setInterval(() => {
            const window = calculateCurrentWindow(genesisBlock);
            setCurrentWindow(window);
        }, 2000);

        return () => clearInterval(interval);
    }, [genesisBlock]);


    useEffect(() => {
        const fetchEarringQueueTxs = async () => {
            try {
                const response = await axios.get<EarringQueueResponse>(
                    `${COORDINADOR_URL}/get-earrings-transactions`
                );
                setEarringTxs(response.data.transactions);
                setError("");
            } catch (err) {
                setError("Error al obtener tareas pendientes de RabbitMQ");
                console.error(err);
            }
        };

        fetchEarringQueueTxs();

        const interval = setInterval(fetchEarringQueueTxs, 10000);

        return () => clearInterval(interval);
    }, []);


    const handleSearchTransaction = async (tx_id: string) => {
        try {
            const response = await axios.get<TransactionResponse>(
                `${COORDINADOR_URL}/get-transaction/${tx_id}`
            );

            setTransaction(response.data.tx);
            setStatus(response.data.status);
            setError("");
        } catch (err) {
            setError("Error al obtener la transacción");
            console.error(err);
        }
    };

    return {
        handleSearchTransaction,
        genesisBlock,
        currentWindow,
        transaction,
        status,
        inProgressTxs,
        earringTxs,
        workers,
        error
    }
}