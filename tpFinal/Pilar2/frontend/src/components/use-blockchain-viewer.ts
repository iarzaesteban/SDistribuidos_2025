import { useState } from "react";
import { COORDINADOR_URL } from "../constants";
import axios from "axios";
import type { Block, GenesisBlockType, LastBlockChainedType } from "../types/types";

export const useBlockchainViewer = () => {
    const [blockchain, setBlockchain] = useState<Block[]>([]);
    const [genesisBlock, setGenesisBlock] = useState<GenesisBlockType>();
    const [lastChainedBlock, setLastChainedBlock] = useState<LastBlockChainedType | null>(null);
    const [createTask, setCreateTask] = useState<boolean>(false);
    const [error, setError] = useState<string>("");

    const cleanData = () => {
        setBlockchain([]);
        setGenesisBlock(undefined);
    }
    const handleCreateTask = () => {
        cleanData();
        setCreateTask(!createTask);
    }

    const fetchBlockchain = async () => {
        try {
            cleanData();
            const response = await axios.get(COORDINADOR_URL + '/blockchain');
            setBlockchain(response.data.Blockchain);
            setError("");
        } catch (err) {
            setError("Error al obtener la blockchain");
            console.log(err);
        }
    };

    const fetchGenesisBlock = async () => {
        try {
            cleanData();
            const response = await axios.get(COORDINADOR_URL + '/genesis-block');
            console.log("La respomse es", response)
            setGenesisBlock(response.data);
            setError("");
        } catch (err) {
            setError("Error al obtener el bloque GENESIS");
            console.log(err);
        }
    };

    const fetchLastChainedBlock = async () => {
        try {
            cleanData();
            const response = await axios.get(COORDINADOR_URL + '/get-last-chained-block');
            setLastChainedBlock(response.data["last-chained-block"]);
            setError("");
        } catch (err) {
            setError("Error al obtener el último bloque encadenado");
            console.error(err);
        }
    };

    return {
        fetchBlockchain,
        fetchGenesisBlock,
        handleCreateTask,
        fetchLastChainedBlock,
        blockchain,
        genesisBlock,
        createTask,
        lastChainedBlock,
        error
    }
};
