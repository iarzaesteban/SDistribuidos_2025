import "./StressTasks.css";
import { useStressTask } from "./use-stress-task";

export const StressTasks = () => {

    const {
        keysAmount,
        tasksAmount,
        response,
        handleSubmit,
        setKeysAmount,
        setTasksAmount
    } = useStressTask();

    return (
        <div className="stress-task-container">
            <h1>Crear tareas - stress</h1>
            {response &&
                <div className="response-container">
                    <p>{response}</p>
                </div>
            }
            <div className="stress-task-form">
                <label htmlFor="keys-amount">Cantidad de pares de claves:</label>
                <input
                    type="number"
                    value={keysAmount}
                    onChange={(e) => setKeysAmount(Number(e.target.value))}
                />

                <label htmlFor="tasks-amount">Cantidad de tareas:</label>
                <input
                    type="number"
                    value={tasksAmount}
                    onChange={(e) => setTasksAmount(Number(e.target.value))}
                />

                <button className="button enviar" onClick={handleSubmit}>
                    Generar y Enviar Tareas
                </button>
            </div>

        </div>
    );
};

export default StressTasks;
