export default function Word({
  children,
  locked,
  predictions,
  rankedPredictions,
  prediction,
  predictionCorrect,
}: {
  children: string;
  locked: boolean;
  predictions: string[];
  rankedPredictions?: Record<string, number>;
  prediction?: string;
  predictionCorrect?: boolean;
}) {
  return (
    <div className={`word ${locked && "locked"}`}>
      <span>{children}</span>
      {prediction && (
        <span
          className={`prediction ${
            predictionCorrect ? "correct" : "incorrect"
          }`}
        >
          {prediction}
        </span>
      )}
      <ul className="predictions">
        {!rankedPredictions
          ? predictions.map((prediction) => (
              <li key={prediction}>{prediction}</li>
            ))
          : Object.entries(rankedPredictions).map(
              ([prediction, probability]) => (
                <li
                  key={prediction}
                  style={{
                    color: `hsl(${120 * probability}, 100%, 45%)`,
                  }}
                >
                  {prediction}
                </li>
              )
            )}
      </ul>
    </div>
  );
}
