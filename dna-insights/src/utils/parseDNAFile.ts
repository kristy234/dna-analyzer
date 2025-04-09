import { Match } from '../types';

type SNPedia = {
  [rsid: string]: {
    [allele1: string]: {
      [allele2: string]: {
        gene: string;
        summary: string;
        magnitude: number;
        repute: string;
      };
    };
  };
};

export async function parseDNAFile(
  file: File,
  snpediaData: SNPedia,
  onProgress?: (percent: number) => void
): Promise<Match[]> {
  console.log('Parsing file...');
  const reader = file.stream().getReader();
  const decoder = new TextDecoder('utf-8');

  const totalBytes = file.size;
  let bytesRead = 0;
  let leftover = '';
  const matches: Match[] = [];
  let lastReportedProgress = 0;
  onProgress?.(lastReportedProgress);

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    bytesRead += value?.length || 0;
    const chunk = decoder.decode(value, { stream: true });
    const lines = (leftover + chunk).split('\n');
    leftover = lines.pop()!;

    for (const line of lines) {
      processLine(line, snpediaData, matches);
    }

    // Only update if progress changes by >=1%
    const currentProgress = Math.floor((bytesRead / totalBytes) * 100);
    if (onProgress && currentProgress !== lastReportedProgress) {
      lastReportedProgress = currentProgress;
      onProgress(currentProgress);
      await new Promise(r => setTimeout(r, 0)); // yield to flush updates
    }
  }

  if (leftover) processLine(leftover, snpediaData, matches);
  onProgress?.(100); // ensure final update
  return matches;
}

function processLine(line: string, snpediaData: SNPedia, matches: Match[]) {
  if (!line || line.startsWith('#')) return;
  let [rsid, , , allele1, allele2] = line.split('\t');
  allele1 = allele1.trim().toUpperCase();
  allele2 = allele2.trim().toUpperCase();
  if (!allele1 || !allele2) return;
  const [a1, a2] = [allele1, allele2].sort();
  var entry = snpediaData[rsid]?.[a1]?.[a2];
  if (entry) {
    const compositeKey = `${rsid}(${a1};${a2})`;
    matches.push({ rsid: compositeKey, ...entry });
  }
}

