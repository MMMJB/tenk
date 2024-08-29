export default function Word({
  children,
  locked,
  predictions,
}: {
  children: string;
  locked: boolean;
  predictions: string[];
}) {
  return (
    <div className={`word ${locked && "locked"}`}>
      <span>{children}</span>
      <ul className="predictions">
        {predictions.map((prediction) => (
          <li key={prediction}>{prediction}</li>
        ))}
      </ul>
    </div>
  );
}
